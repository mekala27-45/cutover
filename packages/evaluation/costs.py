"""Shadow compute prices and explicit analyst-minute assumptions."""
from __future__ import annotations

import math
from typing import Any

from packages.core import Complaint, Decision


def compute_cost(seconds: float, count: int, price_row: dict[str, Any]) -> dict[str, Any]:
    if not math.isfinite(seconds) or seconds < 0 or count <= 0:
        raise ValueError("invalid_compute_measurement")
    if price_row["unit"] != "hour" or not price_row.get("source_digest"):
        raise ValueError("unsupported_or_unproven_price")
    rate = float(price_row["usd"])
    if not math.isfinite(rate) or rate < 0:
        raise ValueError("invalid_price")
    return {
        "usd_per_thousand": seconds / count * 1000 / 3600 * rate,
        "seconds": seconds,
        "count": count,
        "price_row_id": price_row["id"],
        "price_effective_date": price_row["effective_date"],
        "source_digest": price_row["source_digest"],
        "pricing": "shadow",
    }


def analyst_minutes(rows: list[Complaint], decisions: dict[str, Decision],
                    safety_miss: float) -> dict[str, Any]:
    if not rows or safety_miss < 0 or not math.isfinite(safety_miss):
        raise ValueError("invalid_roi_population")
    if {r.odino for r in rows} != set(decisions):
        raise ValueError("incomplete_roi_decisions")
    review = misroutes = missed_safety = 0
    for row in rows:
        decision = decisions[row.odino]
        if decision.action == "send_to_analyst":
            review += 1
        else:
            misroutes += int(decision.queue not in row.label.groups)
            missed_safety += int(row.label.safety)
    minutes = review * 3 + misroutes * 6 + missed_safety * safety_miss
    return {
        "count": len(rows), "reviewed": review, "misroutes": misroutes,
        "missed_safety": missed_safety, "assumed_safety_miss_minutes": safety_miss,
        "analyst_minutes_per_thousand": minutes / len(rows) * 1000,
        "interpretation": "estimate_under_registered_error_costs",
    }
