"""A response is returned only after its receipt is durable."""

from __future__ import annotations

import hmac
import logging
import os
import re
import uuid
from typing import Any

from packages.cascade import unavailable
from packages.core import Feature, digest
from packages.release import is_canary


class BudgetExceeded(Exception):
    pass


class StorageUnavailable(Exception):
    pass


def client_digest(address: str) -> str:
    salt = os.environ.get("CUTOVER_SALT", "")
    if len(salt) < 32:
        raise StorageUnavailable("salt_not_configured")
    return hmac.new(salt.encode(), address.encode(), "sha256").hexdigest()


def log_storage_failure(operation: str, exc: Exception) -> None:
    state = getattr(exc, "sqlstate", None)
    safe_state = state if isinstance(state, str) and re.fullmatch(r"[A-Z0-9]{5}", state) else None
    # Inspect text in memory only; emit fixed categories, never exception text.
    message = str(exc).lower()
    category = "unclassified"
    for token, name in [
        ("password authentication failed", "authentication"),
        ("unsupported startup parameter", "startup_parameter"),
        ("invalid connection option", "connection_option"),
        ("could not translate host name", "dns"),
        ("name or service not known", "dns"),
        ("connection timeout", "timeout"),
        ("timeout expired", "timeout"),
        ("certificate verify failed", "tls_certificate"),
        ("endpoint is disabled", "endpoint_disabled"),
        ('missing "="', "dsn_syntax"),
    ]:
        if token in message:
            category = name
            break
    logging.getLogger(__name__).error(
        "storage_failure operation=%s type=%s sqlstate=%s category=%s",
        operation, type(exc).__name__, safe_state, category,
    )


def connect() -> Any:
    import psycopg

    value = os.environ.get("DATABASE_URL")
    if not value:
        raise StorageUnavailable("database_not_configured")
    connection = psycopg.connect(value, connect_timeout=10)
    try:
        connection.execute("SET LOCAL statement_timeout = '10s'")
    except Exception:
        connection.close()
        raise
    return connection


def triage(feature: Feature, address: str) -> dict[str, Any]:
    from psycopg.types.json import Jsonb

    text_digest = digest(feature.narrative)
    client = client_digest(address)
    receipt = str(uuid.uuid4())
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT stable_digest,canary_digest,canary_weight,killed,version "
                    "FROM cutover.release_state WHERE singleton=true"
                )
                state = cur.fetchone()
                if state is None:
                    raise StorageUnavailable("release_not_initialized")
                stable, canary, weight, killed, version = state
                selected = (
                    canary
                    if canary and not killed and is_canary(text_digest, float(weight))
                    else stable
                )
                cur.execute(
                    """INSERT INTO cutover.client_budget(client_digest,window_start,used)
                    VALUES (%s,date_trunc('hour',now()),1)
                    ON CONFLICT(client_digest,window_start) DO UPDATE
                    SET used=cutover.client_budget.used+1 WHERE cutover.client_budget.used<60
                    RETURNING used""",
                    (client,),
                )
                if cur.fetchone() is None:
                    raise BudgetExceeded()
                # Until a checked model is promoted, all cases explicitly go to a person.
                # This is a guard-only service, not a fitted-model accuracy claim.
                decision = unavailable(feature, selected)
                result = {
                    "receipt_id": receipt,
                    "mode": "guard_only",
                    "model_ready": False,
                    "release": "v1" if selected == stable else "v2",
                    "release_version": version,
                    "text_digest": text_digest,
                    "decision": decision.model_dump(mode="json"),
                }
                cur.execute(
                    """INSERT INTO cutover.triage_log
                    (receipt_id,text_digest,client_digest,release_digest,release_version,decision)
                    VALUES (%s,%s,%s,%s,%s,%s)""",
                    (receipt, text_digest, client, selected, version, Jsonb(result)),
                )
        # psycopg's context manager commits before reaching this return.
        return result
    except BudgetExceeded:
        raise
    except StorageUnavailable:
        raise
    except Exception as exc:
        log_storage_failure("triage", exc)
        raise StorageUnavailable("database_operation_failed") from None


def release_state() -> dict[str, Any]:
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT stable_digest,canary_digest,canary_weight,killed,version,"
                    "updated_at FROM cutover.release_state WHERE singleton=true"
                )
                state = cur.fetchone()
                if not state:
                    raise StorageUnavailable("release_not_initialized")
                cur.execute(
                    "SELECT enabled,reason,created_at,release_version "
                    "FROM cutover.switch_history ORDER BY created_at DESC LIMIT 20"
                )
                history = [
                    {"enabled": r[0], "reason": r[1], "at": r[2].isoformat(), "version": r[3]}
                    for r in cur.fetchall()
                ]
        return {
            "stable_digest": state[0],
            "canary_digest": state[1],
            "canary_weight": float(state[2]),
            "killed": state[3],
            "version": state[4],
            "updated_at": state[5].isoformat(),
            "history": history,
            "model_ready": False,
        }
    except Exception as exc:
        log_storage_failure("release", exc)
        raise StorageUnavailable("release_read_failed") from None
