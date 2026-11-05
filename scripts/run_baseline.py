"""Actual NHTSA floor execution. Never relabel it as an encoder or an LLM."""

from __future__ import annotations

import json
import os
import platform
import time
from pathlib import Path

from packages.cascade import decide
from packages.cascade.tune import select
from packages.core import Complaint, digest
from packages.evaluation import bootstrap, grade
from packages.floor import Floor


def read(path: Path) -> list[Complaint]:
    return [Complaint.model_validate_json(line) for line in path.read_text().splitlines() if line]


def run(root: Path) -> None:
    import joblib

    started = time.perf_counter()
    plan = json.loads((root / "config/plan.json").read_text())
    registration = json.loads((root / "evaluation/registration.json").read_text())
    train = read(root / "private/splits/train.jsonl")
    dev = read(root / "private/splits/development.jsonl")
    model = Floor()
    fitted = model.fit(train, dev)
    dev_predictions = model.predict([r.feature for r in dev])
    thresholds, grid = select(dev, dev_predictions, plan, digest(registration), "development")
    (root / "private/models").mkdir(parents=True, exist_ok=True)
    joblib.dump(model, root / "private/models/floor.joblib")
    reports = {}
    for split in ["test", "shadow"]:
        rows = read(root / f"private/splits/{split}.jsonl")
        predictions = model.predict([r.feature for r in rows])
        decisions = {
            r.odino: decide(r.feature, p, thresholds)
            for r, p in zip(rows, predictions, strict=True)
        }
        reports[split] = grade(rows, decisions)
        reports[split]["queue_interval"] = bootstrap(
            {r.odino: float(decisions[r.odino].queue in r.label.groups) for r in rows}
        )
        # Immutable per-case rows contain no narrative and preserve the denominator.
        path = root / f"results/floor-{split}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(
                    json.dumps(
                        {
                            "odino": r.odino,
                            "received": r.received.isoformat(),
                            "label": r.label.model_dump(mode="json"),
                            "decision": decisions[r.odino].model_dump(),
                            "registration_digest": digest(registration),
                            "text_digest": r.text_digest,
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
    result = {
        "mode": "actual_nhtsa_floor",
        "fit": fitted,
        "thresholds": thresholds.model_dump(),
        "operating_points": grid,
        "reports": reports,
        "elapsed_seconds": time.perf_counter() - started,
        "hardware": platform.platform(),
        "source_commit": os.getenv("GITHUB_SHA"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID"),
        "registration_digest": digest(registration),
        "limitations": [
            "No encoder or recorded language model is included in this floor run.",
            "Independent live model serving is not established by this run.",
        ],
    }
    (root / "results/floor.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1])
