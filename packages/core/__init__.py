"""Strict records: models only see Feature, never Label."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

STATEMENT = (
    "cutover is a portfolio demonstration. Its customer is fictional, and public "
    "NHTSA vehicle complaints stand in for that customer inbox. It is not affiliated "
    "with NHTSA or any vehicle maker, it makes no safety determination, and it is not "
    "for safety, legal or regulatory use. It never closes a complaint: it routes one "
    "to a team or sends it to a person. Its costs are shadow prices from public list prices."
)


def canonical(value: Any) -> bytes:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, allow_inf_nan=False)


class Feature(StrictModel):
    narrative: str = Field(min_length=20, max_length=16000)
    make: str = Field(default="", max_length=100)
    model: str = Field(default="", max_length=256)
    year: int | None = Field(default=None, ge=1886, le=2100)


class Label(StrictModel):
    groups: tuple[str, ...]
    safety: bool


class Complaint(StrictModel):
    odino: str = Field(pattern=r"^\d{1,12}$")
    received: date
    feature: Feature
    label: Label
    layout: Literal[49, 51]
    text_digest: str = Field(pattern=r"^[a-f0-9]{64}$")


Action = Literal["route", "send_to_analyst"]
Reason = Literal[
    "confident_route", "safety_keyword", "safety_probability", "out_of_scope",
    "incumbent_required", "malformed_output", "model_unavailable",
]


class Decision(StrictModel):
    scores: dict[str, float]
    safety_probability: float = Field(ge=0, le=1)
    queue: str
    action: Literal["route", "send_to_analyst"]
    reason: Literal[
        "confident_route",
        "safety_keyword",
        "safety_probability",
        "out_of_scope",
        "incumbent_required",
        "malformed_output",
        "model_unavailable",
    ]
    arm: str
    version_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    compute_ms: float = Field(ge=0)

    @model_validator(mode="after")
    def consistent(self) -> Decision:
        if not self.scores or self.queue not in self.scores:
            raise ValueError("queue_not_in_scores")
        if any(not math.isfinite(v) or not 0 <= v <= 1 for v in self.scores.values()):
            raise ValueError("invalid_score")
        if self.action == "route" and (self.reason != "confident_route" or self.queue == "OTHER"):
            raise ValueError("unsafe_route")
        if self.action == "send_to_analyst" and self.reason == "confident_route":
            raise ValueError("inconsistent_reason")
        return self


class Thresholds(StrictModel):
    routing: float = Field(ge=0, le=1)
    safety: float = Field(ge=0, le=1)
    out_of_scope: float = Field(ge=0, le=1)
    selected_on: Literal["development"]
    registration_digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class Prediction(StrictModel):
    scores: dict[str, float]
    safety_probability: float = Field(ge=0, le=1)
    arm: str
    version_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    compute_ms: float = Field(ge=0)

    @model_validator(mode="after")
    def valid_scores(self) -> Prediction:
        if not self.scores or any(
            not math.isfinite(v) or not 0 <= v <= 1 for v in self.scores.values()
        ):
            raise ValueError("invalid_scores")
        return self
