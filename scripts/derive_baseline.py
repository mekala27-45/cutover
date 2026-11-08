"""Deterministic reporting from actual aggregate evidence, never fixture scores."""

import hashlib
import json
import math
from pathlib import Path


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def derive(root: Path) -> None:
    public = root / "public_results"
    intake = json.loads((public / "intake.json").read_text(encoding="utf-8"))
    floor = json.loads((public / "floor.json").read_text(encoding="utf-8"))
    registration = json.loads((root / "evaluation/registration.json").read_text(encoding="utf-8"))
    lock = json.loads((root / "data/complaints.lock.json").read_text(encoding="utf-8"))
    if floor["registration_digest"] != digest(registration):
        raise ValueError("registration_mismatch")
    if floor["mode"] != "actual_nhtsa_floor" or intake["mode"] != "actual_nhtsa_intake":
        raise ValueError("actual_evidence_required")
    if intake["sources"] != lock["sources"]:
        raise ValueError("source_lock_mismatch")
    for split, report in floor["reports"].items():
        if report["count"] != intake["counts"][split] or report["completed"] != report["count"]:
            raise ValueError("population_mismatch")
        for name in ("queue_hit_rate", "safety_recall", "review_share", "exact_set_match"):
            ratio = report[name]
            if not 0 <= ratio["numerator"] <= ratio["denominator"] or ratio["denominator"] <= 0:
                raise ValueError("invalid_denominator")
            if not math.isclose(ratio["value"], ratio["numerator"] / ratio["denominator"]):
                raise ValueError("ratio_mismatch")
    manifest = json.loads((public / "manifest.json").read_text(encoding="utf-8"))
    manifest["intake_progress"].update(
        workflow_run="https://github.com/mekala27-45/cutover/actions/runs/42118098139",
        mode="actual_nhtsa_intake",
        post_dedup_counts=intake["counts"],
        duplicate_count=intake["duplicate_count"],
        split_digests=intake["split_digests"],
        complete=True,
    )
    for arm in manifest["arms"]:
        if arm["arm"] == "floor":
            arm.update(status="measured_actual", metrics=floor["reports"]["test"])
    manifest["baseline"] = {
        "mode": floor["mode"],
        "source_commit": floor["source_commit"],
        "workflow_run": "https://github.com/mekala27-45/cutover/actions/runs/"
        + floor["workflow_run_id"],
        "evidence": "public_results/floor.json",
        "evidence_digest": digest(floor),
        "intake_digest": digest(intake),
        "reports": floor["reports"],
        "thresholds": floor["thresholds"],
        "fit": floor["fit"],
        "elapsed_seconds": floor["elapsed_seconds"],
        "live_model": False,
    }
    manifest["limitations"] = [
        "Only the TF-IDF floor has completed actual held-out evaluation.",
        "The floor results do not establish encoder or language-model quality.",
        "The live API remains guard-only; no fitted model has been promoted.",
        "Runtime probes use authored text and an untrained classification head.",
        "No measured cost-saving or rollout-success claim is established.",
    ]
    manifest["metrics"] = [
        {
            "arm": "floor", "split": split, "metric": name, "status": "measured",
            "value": report[name]["value"], "denominator": report[name]["denominator"],
            "evidence": "public_results/floor.json",
        }
        for split, report in sorted(floor["reports"].items())
        for name in ("queue_hit_rate", "safety_recall", "review_share", "exact_set_match")
    ]
    manifest.pop("manifest_digest", None)
    manifest["manifest_digest"] = digest(manifest)
    payload = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (public / "manifest.json").write_text(payload, encoding="utf-8", newline="\n")
    (root / "web/public/manifest.json").write_text(payload, encoding="utf-8", newline="\n")
    rows = [
        "# Actual TF-IDF baseline",
        "",
        "This report is derived by scripts/derive_baseline.py from public_results/floor.json.",
        "It describes the floor, not the encoder, language-model arms or live API.",
        "",
        "| Split | Complaints | Queue hit | Queue hit 95% interval | "
        "Safety recall | Review share |",
        "| --- | ---: | ---: | --- | ---: | ---: |",
    ]
    for split, report in sorted(floor["reports"].items()):
        interval = report["queue_interval"]
        rows.append(
            f"| {split} | {report['count']:,} | {report['queue_hit_rate']['value']:.2%} | "
            f"{interval['two_sided_lower']:.2%} to {interval['two_sided_upper']:.2%} | "
            f"{report['safety_recall']['value']:.2%} | {report['review_share']['value']:.2%} |"
        )
    test = floor["reports"]["test"]
    rows += [
        "",
        "The queue interval uses the registered seeded complaint bootstrap. Safety recall",
        "and review share above are point estimates; bounds were not exported for these metrics.",
        "",
        f"Training used {floor['fit']['training_count']:,} complaints and development used "
        f"{floor['fit']['development_count']:,}. Development selected C={floor['fit']['c']}.",
        f"Thresholds: routing={floor['thresholds']['routing']}, "
        f"safety={floor['thresholds']['safety']}, "
        f"out-of-scope={floor['thresholds']['out_of_scope']}.",
        "",
        f"The floor review share is {test['review_share']['value']:.2%}, "
        "above the registered 40% load target. This operating point is not ready for release.",
        "The shipped-system C1-C7 verdicts remain not shown because its required arms are absent.",
        "",
        "The runner discarded private per-case records and model weights "
        "after exporting aggregates.",
        "Aggregate results cannot reproduce paired arm comparisons, new "
        "slices or the trained model.",
        "A future complete run must preserve those in an approved private artifact destination.",
        "",
        "No p95 latency, inference-only throughput, cost saving or ROI is "
        "inferred from total run time.",
        f"Source commit: {floor['source_commit']}.",
        f"Workflow: {manifest['baseline']['workflow_run']}.",
    ]
    report_dir = root / "report"
    report_dir.mkdir(exist_ok=True)
    (report_dir / "baseline.md").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    derive(Path(__file__).resolve().parents[1])
