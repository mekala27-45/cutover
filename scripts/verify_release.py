"""Reject release promotion without complete actual evidence."""
import json
from pathlib import Path

from packages.render import validate_manifest


def verify(root: Path) -> None:
    manifest = json.loads((root / "public_results/manifest.json").read_text())
    validate_manifest(manifest)
    if any(c["verdict"] != "met" for c in manifest["criteria"]):
        raise ValueError("acceptance_criteria_not_met")
    required = ["encoder", "small_recorded", "incumbent_recorded", "cascade"]
    arms = {a["arm"]: a for a in manifest["arms"]}
    if any(arms.get(name, {}).get("status") != "promoted_actual" for name in required):
        raise ValueError("actual_arms_missing")
    if not manifest.get("independent_live_verification"):
        raise ValueError("independent_live_verification_missing")


if __name__ == "__main__":
    verify(Path(__file__).resolve().parents[1])
