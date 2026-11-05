import pytest

from packages.cascade import decide
from packages.evaluation.costs import analyst_minutes, compute_cost
from packages.intake import parse_line
from tests.test_contracts import T, feature, line, pred


def test_shadow_hour_units_and_source():
    row = {"unit": "hour", "usd": "0.192", "id": "cpu",
           "effective_date": "2026-11-01", "source_digest": "a" * 64}
    value = compute_cost(3600, 1000, row)
    assert value["usd_per_thousand"] == pytest.approx(0.192)
    assert value["pricing"] == "shadow"
    with pytest.raises(ValueError):
        compute_cost(10, 0, row)


def test_review_cost_is_not_double_charged():
    row = parse_line(line())
    decision = decide(feature(), pred(0.7), T)
    result = analyst_minutes([row], {row.odino: decision}, 600)
    assert result["analyst_minutes_per_thousand"] == 3000
    assert result["misroutes"] == 0
    with pytest.raises(ValueError, match="incomplete"):
        analyst_minutes([row], {}, 600)
