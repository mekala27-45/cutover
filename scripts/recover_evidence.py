"""Read only the reviewed aggregate outputs of the completed baseline workflow."""

import json
from pathlib import Path


def validate_public(value: object) -> None:
    if isinstance(value, dict):
        if set(value) & {"odino", "narrative", "sample_ids", "client_digest"}:
            raise ValueError("private_field_in_aggregate")
        for child in value.values():
            validate_public(child)
    elif isinstance(value, list):
        for child in value:
            validate_public(child)


def run() -> None:
    for name in ("intake.json", "floor.json"):
        value = json.loads((Path("recovered") / name).read_text(encoding="utf-8"))
        validate_public(value)
        print("CUTOVER_EVIDENCE " + name + " " + json.dumps(value, separators=(",", ":")))


if __name__ == "__main__":
    run()
