"""Actual aggregate consistency and deterministic report regression checks."""

import json
import shutil
from pathlib import Path

import pytest

from scripts.derive_baseline import derive

ROOT = Path(__file__).resolve().parents[1]


def fixture(root):
    for name in (
        "public_results/intake.json",
        "public_results/floor.json",
        "public_results/manifest.json",
        "evaluation/registration.json",
        "data/complaints.lock.json",
    ):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    (root / "web/public").mkdir(parents=True)


def test_report_rederives_without_drift(tmp_path):
    fixture(tmp_path)
    derive(tmp_path)
    for name in ("public_results/manifest.json", "web/public/manifest.json", "report/baseline.md"):
        assert (tmp_path / name).read_bytes() == (ROOT / name).read_bytes()
    before = (tmp_path / "public_results/manifest.json").read_bytes()
    derive(tmp_path)
    assert (tmp_path / "public_results/manifest.json").read_bytes() == before


@pytest.mark.parametrize("change", ["denominator", "population", "registration", "mode"])
def test_reject_corrupted_aggregate(tmp_path, change):
    fixture(tmp_path)
    target = tmp_path / "public_results/floor.json"
    data = json.loads(target.read_text())
    if change == "denominator":
        data["reports"]["test"]["queue_hit_rate"]["denominator"] = 1
    elif change == "population":
        data["reports"]["test"]["count"] -= 1
    elif change == "registration":
        data["registration_digest"] = "bad"
    else:
        data["mode"] = "fixture"
    target.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        derive(tmp_path)
