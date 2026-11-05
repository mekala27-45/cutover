"""Stable canary assignments, monitor decisions and digest-checked rollback."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any, cast


def is_canary(key: str, weight: float) -> bool:
    if not key or not 0 <= weight <= 1:
        raise ValueError("invalid_assignment")
    return int(hashlib.sha256(key.encode()).hexdigest()[:16], 16) / 2**64 < weight


def psi(reference: list[int], observed: list[int]) -> float:
    if len(reference) != len(observed) or not reference or min(reference + observed) < 0:
        raise ValueError("invalid_histograms")
    if sum(reference) == 0 or sum(observed) == 0:
        raise ValueError("empty_histogram")
    # Jeffreys smoothing avoids infinite values at sparse boundaries.
    n = len(reference)
    pairs = [
        ((a + 0.5) / (sum(reference) + 0.5 * n), (b + 0.5) / (sum(observed) + 0.5 * n))
        for a, b in zip(reference, observed, strict=True)
    ]
    return sum((b - a) * math.log(b / a) for a, b in pairs)


def alarms(window: dict[str, float | None], rules: dict[str, Any]) -> dict[str, Any]:
    required = ["agreement", "review_share_delta", "safety_flag_delta", "psi"]
    if any(window.get(k) is None for k in required):
        return {"state": "insufficient", "trip": False, "alarms": []}
    hits = []
    if (
        window.get("safety_recall") is not None
        and window["safety_recall"] < rules["safety_recall_min"]
    ):
        hits.append("safety")
    if window["agreement"] < rules["agreement_min"]:
        hits.append("agreement")
    if abs(cast(float, window["review_share_delta"])) > rules["review_share_delta"]:
        hits.append("review_share")
    if abs(cast(float, window["safety_flag_delta"])) > rules["safety_flag_delta"]:
        hits.append("safety_flag")
    if window["psi"] > rules["psi_max"]:
        hits.append("score_stability")
    return {"state": "evaluated", "trip": "safety" in hits or len(hits) >= 2, "alarms": hits}


def restore(registry: Path, digest: str, destination: Path) -> None:
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("invalid_digest")
    source = registry / digest
    content = source.read_bytes()
    if hashlib.sha256(content).hexdigest() != digest:
        raise ValueError("artifact_digest_mismatch")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".pending")
    temporary.write_bytes(content)
    temporary.replace(destination)
