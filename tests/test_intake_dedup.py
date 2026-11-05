from datetime import date

import pytest

from packages.intake import parse_line
from packages.intake.dedup import jaccard, registered_sample, shingles, temporal_dedup
from tests.test_contracts import line


def test_later_exact_duplicate_removed():
    a = parse_line(line()).model_copy(update={"received": date(2023, 1, 1)})
    b = a.model_copy(update={"odino": "456", "received": date(2024, 1, 1)})
    splits, drops = temporal_dedup([b, a])
    assert len(splits["train"]) == 1 and "development" not in splits
    assert drops == [{"odino": "456", "reason": "duplicate", "earlier": "123456"}]


def test_near_duplicate_exact_jaccard():
    a = shingles("one two three four five six seven eight nine ten " * 30)
    assert jaccard(a, a) == 1


def test_registered_sample_refuses_insufficient():
    with pytest.raises(ValueError):
        registered_sample([parse_line(line())], 2)


def test_sample_order_deterministic():
    a = parse_line(line())
    rows = [a.model_copy(update={"odino": str(i)}) for i in range(100)]
    assert registered_sample(rows, 20) == registered_sample(list(reversed(rows)), 20)
