"""Operating points selected on development only, including interior comparisons."""

from __future__ import annotations

from itertools import product
from typing import Any

from packages.cascade import decide
from packages.core import Complaint, Prediction, Thresholds


def select(
    rows: list[Complaint],
    predictions: list[Prediction],
    plan: dict[str, Any],
    registration: str,
    split: str,
) -> tuple[Thresholds, list[dict[str, Any]]]:
    if split != "development" or not rows or len(rows) != len(predictions):
        raise ValueError("development_only_selection")
    grid = plan["threshold_grids"]
    records = []
    for routing, safety, ood in product(grid["routing"], grid["safety"], grid["out_of_scope"]):
        if ood > routing:
            continue
        t = Thresholds(
            routing=float(routing),
            safety=float(safety),
            out_of_scope=float(ood),
            selected_on="development",
            registration_digest=registration,
        )
        loss = 0.0
        for row, pred in zip(rows, predictions, strict=True):
            d = decide(row.feature, pred, t)
            costs = plan["costs_minutes"]
            loss += (
                costs["review"]
                if d.action == "send_to_analyst"
                else (
                    costs["misroute"] * int(d.queue not in row.label.groups)
                    + costs["safety_miss"] * int(row.label.safety)
                )
            )
        records.append(
            {
                "routing": routing,
                "safety": safety,
                "out_of_scope": ood,
                "analyst_minutes": loss,
                "count": len(rows),
            }
        )
    best = min(
        records,
        key=lambda x: (x["analyst_minutes"], x["safety"], -x["routing"], -x["out_of_scope"]),
    )
    chosen = Thresholds(
        routing=float(best["routing"]),
        safety=float(best["safety"]),
        out_of_scope=float(best["out_of_scope"]),
        selected_on="development",
        registration_digest=registration,
    )
    return chosen, records
