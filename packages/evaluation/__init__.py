"""Independent labels grade decisions; missing attempts remain failures."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Any

from packages.core import Complaint, Decision


def ratio(numerator: int, denominator: int) -> dict[str, Any]:
    return {
        "value": numerator / denominator if denominator else None,
        "numerator": numerator,
        "denominator": denominator,
    }


def grade(rows: list[Complaint], decisions: dict[str, Decision]) -> dict[str, Any]:
    if not rows:
        raise ValueError("empty_evaluation")
    ids = [r.odino for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate_odino")
    if set(decisions) - set(ids):
        raise ValueError("unexpected_prediction")
    hit = reviewed = safety_reviewed = safety_total = predicted_safety = 0
    group_stats: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    exact = 0
    calibration: list[tuple[float, bool]] = []
    for row in rows:
        d = decisions.get(row.odino)
        safety_total += int(row.label.safety)
        if d is None:
            for g in row.label.groups:
                group_stats[g][2] += 1
            continue
        hit += int(d.queue in row.label.groups)
        reviewed += int(d.action == "send_to_analyst")
        safety_reviewed += int(row.label.safety and d.action == "send_to_analyst")
        predicted_safety += int(d.safety_probability >= 0.5)
        predicted = {g for g, p in d.scores.items() if p >= 0.5}
        actual = set(row.label.groups)
        exact += int(predicted == actual)
        for g in actual | predicted:
            group_stats[g][0] += int(g in actual and g in predicted)
            group_stats[g][1] += int(g not in actual and g in predicted)
            group_stats[g][2] += int(g in actual and g not in predicted)
        calibration.append((d.scores[d.queue], d.queue in actual))
    f1 = {
        g: 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
        for g, (tp, fp, fn) in sorted(group_stats.items())
    }
    valid = [x for x in f1.values() if x is not None]
    return {
        "count": len(rows),
        "completed": len(decisions),
        "missing": sorted(set(ids) - set(decisions)),
        "queue_hit_rate": ratio(hit, len(rows)),
        "exact_set_match": ratio(exact, len(rows)),
        "safety_recall": ratio(safety_reviewed, safety_total),
        "review_share": ratio(reviewed, len(rows)),
        "review_precision": ratio(safety_reviewed, reviewed),
        "macro_f1": sum(valid) / len(valid) if valid else None,
        "group_f1": f1,
        "ece": ece(calibration),
        "per_group_recall": {
            g: ratio(tp, tp + fn) for g, (tp, fp, fn) in sorted(group_stats.items())
        },
    }


def ece(rows: list[tuple[float, bool]], bins: int = 10) -> float | None:
    if not rows:
        return None
    if bins < 1:
        raise ValueError("invalid_bins")
    buckets: dict[int, list[tuple[float, bool]]] = defaultdict(list)
    for probability, correct in rows:
        if not 0 <= probability <= 1:
            raise ValueError("invalid_probability")
        buckets[min(bins - 1, int(probability * bins))].append((probability, correct))
    return sum(
        abs(sum(p for p, _ in b) / len(b) - sum(c for _, c in b) / len(b)) * len(b) / len(rows)
        for b in buckets.values()
    )


def bootstrap(values: dict[str, float], seed: int = 23, samples: int = 10000) -> dict[str, float]:
    if not values or samples < 100:
        raise ValueError("insufficient_bootstrap")
    ordered = [values[k] for k in sorted(values)]
    import numpy as np

    # Multinomial counts are exactly the empirical bootstrap distribution.
    # They avoid allocating samples x population for binary/paired metrics.
    unique, counts = np.unique(ordered, return_counts=True)
    rng = np.random.default_rng(seed)
    means = sorted(
        (
            rng.multinomial(len(ordered), counts / len(ordered), size=samples)
            @ unique
            / len(ordered)
        ).tolist()
    )
    return {
        "estimate": sum(ordered) / len(ordered),
        "lower95": means[int(0.05 * samples)],
        "upper95": means[min(samples - 1, int(0.95 * samples))],
        "two_sided_lower": means[int(0.025 * samples)],
        "two_sided_upper": means[min(samples - 1, int(0.975 * samples))],
    }


def paired_difference(a: dict[str, float], b: dict[str, float], **kwargs: Any) -> dict[str, float]:
    if set(a) != set(b):
        raise ValueError("unpaired_populations")
    return bootstrap({k: a[k] - b[k] for k in a}, **kwargs)


def bh(pvalues: dict[str, float]) -> dict[str, float]:
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in pvalues.values()):
        raise ValueError("invalid_pvalue")
    ranked = sorted(pvalues, key=lambda k: (pvalues[k], k))
    adjusted, last = {}, 1.0
    for i in range(len(ranked) - 1, -1, -1):
        key = ranked[i]
        last = min(last, pvalues[key] * len(ranked) / (i + 1))
        adjusted[key] = last
    return {k: adjusted[k] for k in sorted(adjusted)}


def verdict(
    value: float | None,
    threshold: float,
    operator: str,
    lower: float | None = None,
    upper: float | None = None,
) -> str:
    if value is None:
        return "not_shown"
    lo, hi = (value if lower is None else lower), (value if upper is None else upper)
    if not all(math.isfinite(v) for v in (value, threshold, lo, hi)) or not lo <= value <= hi:
        raise ValueError("invalid_interval")
    if operator == "gte":
        return "met" if lo >= threshold else "not_met" if hi < threshold else "not_shown"
    if operator == "lte":
        return "met" if hi <= threshold else "not_met" if lo > threshold else "not_shown"
    raise ValueError("invalid_operator")
