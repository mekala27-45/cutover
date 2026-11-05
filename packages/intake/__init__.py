"""Privacy boundary based on the NHTSA CMPL layout read on 2026-11-05."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from datetime import datetime

from packages.core import Complaint, Feature, Label, digest


class Quarantine(ValueError):
    """Only the reason may be logged. Never retain the original line."""


def parse_line(line: str) -> Complaint:
    fields = line.rstrip("\r\n").split("\t")
    if len(fields) not in (49, 51):
        raise Quarantine("field_count")
    # Construct only allowlisted fields. All remaining columns die in this frame.
    if fields[45].strip() != "V":
        raise Quarantine("non_vehicle")
    narrative = fields[19].strip()
    if len(narrative) < 20 or len(narrative) > 16000:
        raise Quarantine("narrative_length")
    try:
        received = datetime.strptime(fields[16].strip(), "%Y%m%d").date()
        crash, fire = fields[6].strip(), fields[8].strip()
        if crash not in ("Y", "N") or fire not in ("Y", "N"):
            raise ValueError("unknown_safety")
        injured, deaths = int(fields[9]), int(fields[10])
        if min(injured, deaths) < 0:
            raise ValueError("negative_count")
        year_text = fields[5].strip()
        year = None if year_text in ("", "9999") else int(year_text)
        group = fields[11].split(":")[0].strip()
        if not group:
            raise ValueError("empty_group")
        feature = Feature(
            narrative=narrative, make=fields[3].strip(), model=fields[4].strip(), year=year
        )
        return Complaint(
            odino=fields[1].strip(),
            received=received,
            feature=feature,
            label=Label(
                groups=(group,), safety=crash == "Y" or fire == "Y" or injured > 0 or deaths > 0
            ),
            layout=49 if len(fields) == 49 else 51,
            text_digest=digest(normalize(narrative)),
        )
    except (ValueError, TypeError):
        raise Quarantine("invalid_allowed_field") from None


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def group_rows(rows: Iterable[Complaint]) -> tuple[list[Complaint], dict[str, int]]:
    grouped: dict[str, list[Complaint]] = defaultdict(list)
    for row in rows:
        grouped[row.odino].append(row)
    accepted: list[Complaint] = []
    counts: Counter[str] = Counter()
    for odino, variants in sorted(grouped.items()):
        first = variants[0]
        if any(
            (v.received, v.text_digest, v.feature, v.label.safety)
            != (first.received, first.text_digest, first.feature, first.label.safety)
            for v in variants
        ):
            counts["conflicting_odino"] += len(variants)
            continue
        groups = tuple(sorted({g for v in variants for g in v.label.groups}))
        accepted.append(
            first.model_copy(update={"label": Label(groups=groups, safety=first.label.safety)})
        )
        counts["component_rows_grouped"] += len(variants) - 1
    return accepted, dict(counts)


def split_name(row: Complaint) -> str | None:
    d = row.received.isoformat()
    if "2020-01-01" <= d <= "2020-12-31":
        return "discovery"
    if "2021-01-01" <= d <= "2023-12-31":
        return "train"
    if "2024-01-01" <= d <= "2024-06-30":
        return "development"
    if "2024-07-01" <= d <= "2025-12-31":
        return "test"
    if "2026-01-01" <= d <= "2026-12-31":
        return "shadow"
    return None


def label_map(train: list[Complaint], minimum: int = 500) -> dict[str, str]:
    if not train or minimum < 1:
        raise ValueError("empty_training_or_invalid_minimum")
    counts = Counter(g for row in train for g in set(row.label.groups))
    return {g: g if n >= minimum else "OTHER" for g, n in sorted(counts.items())}


def apply_labels(row: Complaint, mapping: dict[str, str]) -> Complaint:
    label = Label(
        groups=tuple(sorted({mapping.get(g, "OTHER") for g in row.label.groups})),
        safety=row.label.safety,
    )
    return row.model_copy(update={"label": label})
