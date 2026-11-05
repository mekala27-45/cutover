import pytest

from packages.core import digest
from packages.render import validate_manifest
from scripts.check_gates import run, scan_text


def manifest():
    m = {
        "schema_version": 1,
        "criteria": [
            {"id": f"C{i}", "verdict": "not_shown", "reason": "no run"} for i in range(1, 8)
        ],
        "metrics": [],
    }
    return m | {"manifest_digest": digest(m)}


def test_gate_clean():
    assert scan_text("Evidence is unavailable.", True) == []


def test_gate_violation():
    assert scan_text("A" + chr(0x2014) + "B") == ["em_dash"]


def test_gate_empty(tmp_path):
    with pytest.raises(ValueError):
        run(tmp_path)


def test_claim_clean():
    validate_manifest(manifest())


def test_claim_tamper():
    m = manifest()
    m["criteria"][0]["verdict"] = "met"
    with pytest.raises(ValueError):
        validate_manifest(m)


def test_claim_empty():
    with pytest.raises(ValueError):
        validate_manifest({})
