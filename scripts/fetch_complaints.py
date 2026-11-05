"""Fetch NHTSA archives without ever writing raw records or raw archives."""

from __future__ import annotations

import hashlib
import io
import json
import re
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

from packages.core import digest
from packages.intake import Quarantine, apply_labels, group_rows, label_map, parse_line
from packages.intake.dedup import registered_sample, temporal_dedup

BASE = "https://static.nhtsa.gov/odi/ffdd/cmpl/"
CATALOG = "https://www.nhtsa.gov/nhtsa-datasets-and-apis"
MAX_ARCHIVE = 600_000_000


def get(url: str) -> bytes:
    if not (url.startswith(BASE) or url == CATALOG):
        raise ValueError("source_not_allowlisted")
    req = urllib.request.Request(url, headers={"User-Agent": "Cutover-portfolio-source-check/0.1"})
    with urllib.request.urlopen(req, timeout=90) as response:
        data = response.read(MAX_ARCHIVE + 1)
    if len(data) > MAX_ARCHIVE:
        raise ValueError("source_byte_budget_exceeded")
    return data


def fetch(root: Path) -> dict:
    layout = get(BASE + "CMPL.txt")
    if b"COMPLAINTS_RECEIVED_YYYY-YYYY.zip" not in layout:
        raise ValueError("unrecognized_source_layout_contract")
    catalog = json.loads((root / "config/source-catalog.json").read_text())
    if catalog["source"] != CATALOG:
        raise ValueError("invalid_catalog_source")
    listing = "\n".join(catalog["names"])
    names = sorted(set(re.findall(r"COMPLAINTS_RECEIVED_\d{4}-\d{4}\.zip", listing, re.I)))
    names = [n for n in names if int(re.search(r"(\d{4})-(\d{4})", n)[2]) >= 2020]
    if not names:
        raise ValueError("archive_names_not_discovered")
    locks, rows, dropped, layouts = [], [], Counter(), Counter()
    for name in names:
        content = get(BASE + name)
        locks.append(
            {
                "url": BASE + name,
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            members = [m for m in archive.infolist() if not m.is_dir()]
            if sum(m.file_size for m in members) > 6_000_000_000:
                raise ValueError("uncompressed_byte_budget")
            for member in members:
                with archive.open(member) as stream:
                    for raw in stream:
                        if len(raw) > 100_000:
                            dropped["row_byte_budget"] += 1
                            continue
                        try:
                            row = parse_line(raw.decode("utf-8", errors="strict"))
                            rows.append(row)
                            layouts[row.layout] += 1
                        except UnicodeError:
                            dropped["encoding"] += 1
                        except Quarantine as exc:
                            dropped[str(exc)] += 1
        del content
    print(json.dumps({"stage": "parsed", "accepted_component_rows": len(rows),
                      "layouts_seen": dict(layouts), "sources": locks}), flush=True)
    grouped, group_drops = group_rows(rows)
    del rows
    print(json.dumps({"stage": "grouped", "complaints": len(grouped)}), flush=True)
    dropped.update(group_drops)
    splits, duplicates = temporal_dedup(grouped)
    print(json.dumps({"stage": "deduplicated", "counts": {k: len(v) for k,v in splits.items()},
                      "duplicates": len(duplicates)}), flush=True)
    mapping = label_map(splits.get("train", []))
    plan = json.loads((root / "config/plan.json").read_text())
    sample_ids = {}
    for name, count in plan["samples"].items():
        if isinstance(count, int):
            sample_ids[name] = registered_sample(splits.get(name, []), count, plan["seed"])
    target = root / "private/splits"
    target.mkdir(parents=True, exist_ok=True)
    split_digests = {}
    # Only whitelisted records reach disk. Public artifacts exclude this directory.
    for name, records in splits.items():
        mapped = [apply_labels(r, mapping) for r in records]
        payload = "".join(r.model_dump_json() + "\n" for r in mapped)
        (target / f"{name}.jsonl").write_text(payload, encoding="utf-8")
        split_digests[name] = hashlib.sha256(payload.encode()).hexdigest()
    result = {
        "mode": "actual_nhtsa_intake",
        "sources": locks,
        "layout_document_sha256": hashlib.sha256(layout).hexdigest(),
        "catalog_sha256": hashlib.sha256(listing.encode()).hexdigest(),
        "layouts_seen": dict(layouts),
        "counts": {k: len(v) for k, v in splits.items()},
        "dropped": dict(dropped),
        "duplicate_count": len(duplicates),
        "label_mapping": mapping,
        "label_mapping_digest": digest(mapping),
        "sample_ids": sample_ids,
        "split_digests": split_digests,
    }
    (root / "results").mkdir(exist_ok=True)
    (root / "results/intake.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    discovery = {
        "by_month": dict(Counter(r.received.isoformat()[:7] for r in grouped)),
        "by_group": dict(Counter(g for r in grouped for g in r.label.groups)),
        "safety_count": sum(r.label.safety for r in grouped),
        "multi_group_count": sum(len(r.label.groups) > 1 for r in grouped),
    }
    (root / "results/discovery.json").write_text(
        json.dumps(discovery, sort_keys=True, indent=2) + "\n"
    )
    return result


if __name__ == "__main__":
    fetch(Path(__file__).resolve().parents[1])
