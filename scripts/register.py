"""Freeze criteria and configuration before any test scoring."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = ["config/criteria.yaml", "config/plan.json"]


def current():
    return {
        p: hashlib.sha256(
            json.dumps(
                json.loads((ROOT / p).read_text()), sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        for p in PATHS
    }


if __name__ == "__main__":
    path = ROOT / "evaluation/registration.json"
    records = current()
    payload = {
        "files": records,
        "registered_on": "2026-11-05",
        "status": "before_any_test_scoring",
        "real_customer_signature": False,
    }
    if "--check" in sys.argv:
        if not path.exists() or json.loads(path.read_text()) != payload:
            raise SystemExit("registration_changed_or_missing")
    else:
        if path.exists():
            raise SystemExit("refusing_to_replace_registration")
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("registration verified")
