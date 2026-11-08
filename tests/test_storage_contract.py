"""Transaction mechanics with an independent spy, not a live persistence claim."""

from datetime import UTC, datetime

import pytest

from packages.api import store
from packages.core import Feature


class Cursor:
    def __init__(self, exhausted=False, fail_insert=False):
        self.exhausted = exhausted
        self.fail_insert = fail_insert
        self.statement = ""
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        self.statement = sql
        self.calls.append((sql, params))
        if self.fail_insert and "INSERT INTO cutover.triage_log" in sql:
            raise RuntimeError("simulated storage fault")

    def fetchone(self):
        if "release_state" in self.statement:
            state = ("a" * 64, None, 0.0, False, 7)
            return state + (datetime.now(UTC),) if "updated_at" in self.statement else state
        return None if self.exhausted else (1,)

    def fetchall(self):
        return [(True, "synthetic kill test", datetime.now(UTC), 7)]


class Connection:
    def __init__(self, cursor):
        self.cur = cursor
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *args):
        self.committed = exc_type is None
        self.rolled_back = exc_type is not None
        return False

    def cursor(self):
        return self.cur


def setup(monkeypatch, **options):
    connection = Connection(Cursor(**options))
    monkeypatch.setenv("CUTOVER_SALT", "test-only-salt-" * 4)
    monkeypatch.setattr(store, "connect", lambda: connection)
    return connection


def test_receipt_commits_before_return_and_omits_text(monkeypatch):
    connection = setup(monkeypatch)
    narrative = "Authored private test narrative with a distinctive marker."
    result = store.triage(Feature(narrative=narrative), "192.0.2.1")
    assert connection.committed and not connection.rolled_back
    assert result["decision"]["action"] == "send_to_analyst"
    assert "FOR SHARE" not in connection.cur.calls[0][0]
    logged = connection.cur.calls[-1][1][-1].obj
    assert narrative not in str(logged)
    assert "192.0.2.1" not in str(connection.cur.calls)


def test_insert_failure_rolls_back_and_refuses_response(monkeypatch):
    connection = setup(monkeypatch, fail_insert=True)
    with pytest.raises(store.StorageUnavailable):
        store.triage(
            Feature(narrative="An authored narrative for persistence failure."), "192.0.2.2"
        )
    assert connection.rolled_back and not connection.committed


def test_budget_refusal_has_no_log_insert(monkeypatch):
    connection = setup(monkeypatch, exhausted=True)
    with pytest.raises(store.BudgetExceeded):
        store.triage(Feature(narrative="An authored narrative for request budget."), "192.0.2.3")
    assert not any("INSERT INTO cutover.triage_log" in sql for sql, _ in connection.cur.calls)


def test_missing_secrets_refuse(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("CUTOVER_SALT", raising=False)
    with pytest.raises(store.StorageUnavailable):
        store.connect()
    with pytest.raises(store.StorageUnavailable):
        store.client_digest("192.0.2.4")


def test_release_reader_returns_history(monkeypatch):
    setup(monkeypatch)
    result = store.release_state()
    assert result["version"] == 7
    assert result["history"][0]["enabled"] is True


def test_client_hmac_changes_with_salt(monkeypatch):
    monkeypatch.setenv("CUTOVER_SALT", "a" * 32)
    first = store.client_digest("192.0.2.5")
    monkeypatch.setenv("CUTOVER_SALT", "b" * 32)
    assert store.client_digest("192.0.2.5") != first


def test_storage_diagnostics_never_log_exception_message(caplog):
    class PrivateError(Exception):
        sqlstate = "08006"

    store.log_storage_failure("release", PrivateError("private-marker-do-not-log"))
    assert "08006" in caplog.text
    assert "private-marker-do-not-log" not in caplog.text


def test_storage_diagnostics_reject_nonstandard_sqlstate(caplog):
    class PrivateError(Exception):
        sqlstate = "private-marker"

    store.log_storage_failure("release", PrivateError("secret-message"))
    assert "private-marker" not in caplog.text
    assert "secret-message" not in caplog.text


def test_pooler_timeout_is_set_inside_transaction(monkeypatch):
    import psycopg

    class SpyConnection:
        closed = False

        def execute(self, sql):
            self.sql = sql

        def close(self):
            self.closed = True

    connection = SpyConnection()
    observed = {}

    def connect(value, **kwargs):
        observed.update(kwargs)
        return connection

    monkeypatch.setenv("DATABASE_URL", "test-only-dsn")
    monkeypatch.setattr(psycopg, "connect", connect)
    assert store.connect() is connection
    assert "options" not in observed
    assert observed["connect_timeout"] == 10
    assert connection.sql == "SET LOCAL statement_timeout = '10s'"
    assert not connection.closed
