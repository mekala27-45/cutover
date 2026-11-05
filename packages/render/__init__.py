"""Reports accept only digested evidence, never handwritten measured values."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.core import STATEMENT, digest


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != 1 or "criteria" not in manifest:
        raise ValueError("missing_manifest")
    body = {k: v for k, v in manifest.items() if k != "manifest_digest"}
    if digest(body) != manifest.get("manifest_digest"):
        raise ValueError("manifest_digest_mismatch")
    if {c["id"] for c in manifest["criteria"]} != {f"C{i}" for i in range(1, 8)}:
        raise ValueError("incomplete_criteria")
    for metric in manifest.get("metrics", []):
        if metric["status"] == "measured":
            if metric.get("denominator", 0) <= 0 or not metric.get("evidence"):
                raise ValueError("unsubstantiated_metric")
    for row in manifest["criteria"]:
        if row["verdict"] != "not_shown" and not row.get("evidence"):
            raise ValueError("criterion_without_evidence")


def render(manifest: dict[str, Any], root: Path) -> None:
    validate_manifest(manifest)
    rows = ["| Criterion | Verdict | Evidence |", "| --- | --- | --- |"]
    rows += [
        f"| {c['id']} | {c['verdict'].replace('_', ' ')} | {c['reason']} |"
        for c in manifest["criteria"]
    ]
    output = "# Cutover criteria\n\n" + "\n".join(rows) + "\n\n" + STATEMENT + "\n"
    (root / "report").mkdir(exist_ok=True)
    (root / "report/criteria.md").write_text(output, encoding="utf-8")
    (root / "web/public").mkdir(parents=True, exist_ok=True)
    (root / "web/public/manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
