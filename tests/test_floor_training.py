"""Synthetic model mechanics only; never real-data accuracy evidence."""

from datetime import date

import joblib
import pytest

from packages.cascade.tune import select
from packages.core import Feature, Label, digest
from packages.floor import Floor
from packages.intake import parse_line
from tests.test_contracts import line


def rows(count, year):
    result = []
    for i in range(count):
        steering = i % 2 == 0
        narrative = (
            "The steering wheel column becomes stiff during parking."
            if steering
            else "The brake pedal cylinder loses pressure during stopping."
        )
        if i % 3 == 0:
            narrative += " Smoke appeared and the driver was injured."
        base = parse_line(line())
        result.append(
            base.model_copy(
                update={
                    "odino": str(year * 1000 + i),
                    "received": date(year, 2, 1),
                    "feature": Feature(narrative=narrative),
                    "label": Label(
                        groups=("STEERING" if steering else "BRAKES",), safety=i % 3 == 0
                    ),
                    "text_digest": digest(narrative),
                }
            )
        )
    return result


def test_floor_fits_calibrates_and_roundtrips(tmp_path):
    model = Floor()
    train, dev = rows(36, 2023), rows(12, 2024)
    report = model.fit(train, dev)
    assert report["training_count"] == len(train)
    assert len(report["candidate_losses"]) == 3
    predicted = model.predict([r.feature for r in dev])
    assert len(predicted) == len(dev)
    assert all(p.arm == "floor" for p in predicted)
    assert all(
        max(p.scores, key=p.scores.get) in r.label.groups
        for p, r in zip(predicted, dev, strict=True)
    )
    target = tmp_path / "floor.joblib"
    joblib.dump(model, target)
    restored = joblib.load(target)
    second = restored.predict([r.feature for r in dev])
    assert [p.scores for p in predicted] == [p.scores for p in second]
    assert [p.safety_probability for p in predicted] == [p.safety_probability for p in second]


def test_floor_refuses_unfitted_and_empty():
    with pytest.raises(ValueError, match="not_fitted"):
        Floor().predict([Feature(narrative="An authored narrative for a model test.")])
    with pytest.raises(ValueError, match="missing_training"):
        Floor().fit([], [])


def test_thresholds_are_selected_on_development_only():
    from tests.test_contracts import pred

    dev = rows(12, 2024)
    predictions = [pred(0.75, 0.2 if r.label.safety else 0.01) for r in dev]
    plan = {
        "threshold_grids": {
            "routing": [0.5, 0.8],
            "safety": [0.1, 0.3],
            "out_of_scope": [0.1, 0.6],
        },
        "costs_minutes": {"review": 3, "misroute": 6, "safety_miss": 600},
    }
    selected, comparisons = select(dev, predictions, plan, "a" * 64, "development")
    assert selected.selected_on == "development"
    assert comparisons and all(v["out_of_scope"] <= v["routing"] for v in comparisons)
    assert any(v["safety"] == 0.1 for v in comparisons)
    assert any(v["safety"] == 0.3 for v in comparisons)
    with pytest.raises(ValueError, match="development_only"):
        select(dev, predictions, plan, "a" * 64, "test")
