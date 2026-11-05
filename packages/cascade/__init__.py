"""Decision policy is independent of model output and cannot close a case."""

from __future__ import annotations

import re

from packages.core import Action, Decision, Feature, Prediction, Reason, Thresholds

SAFETY = re.compile(
    r"\b(crash(?:ed|es|ing)?|collisi(?:on|ons)|fire|fires|smok(?:e|ing)|"
    r"injur(?:y|ies|ed)|hospital(?:ized)?|kill(?:ed|ing)?|death|fatal(?:ity|ities)?)\b",
    re.I,
)


def decide(
    feature: Feature,
    prediction: Prediction,
    thresholds: Thresholds,
    incumbent: Prediction | None = None,
) -> Decision:
    scores = prediction.scores
    queue = sorted(scores, key=lambda g: (-scores[g], g))[0]
    action: Action = "route"
    reason: Reason = "confident_route"
    if SAFETY.search(feature.narrative):
        action, reason = "send_to_analyst", "safety_keyword"
    elif prediction.safety_probability >= thresholds.safety:
        action, reason = "send_to_analyst", "safety_probability"
    elif queue == "OTHER" or scores[queue] < thresholds.out_of_scope:
        action, reason = "send_to_analyst", "out_of_scope"
    elif scores[queue] < thresholds.routing:
        if incumbent is None:
            action, reason = "send_to_analyst", "incumbent_required"
        else:
            queue = sorted(incumbent.scores, key=lambda g: (-incumbent.scores[g], g))[0]
            scores = incumbent.scores
            if incumbent.safety_probability >= thresholds.safety:
                action, reason = "send_to_analyst", "safety_probability"
            elif queue == "OTHER":
                action, reason = "send_to_analyst", "out_of_scope"
    return Decision(
        scores=scores,
        queue=queue,
        action=action,
        reason=reason,
        safety_probability=max(
            prediction.safety_probability, incumbent.safety_probability if incumbent else 0.0
        ),
        arm=prediction.arm + "_cascade",
        version_digest=prediction.version_digest,
        compute_ms=prediction.compute_ms + (incumbent.compute_ms if incumbent else 0.0),
    )


def unavailable(feature: Feature, version: str) -> Decision:
    return Decision(
        scores={"OTHER": 0.0},
        safety_probability=1.0,
        queue="OTHER",
        action="send_to_analyst",
        reason="safety_keyword" if SAFETY.search(feature.narrative) else "model_unavailable",
        arm="unavailable",
        version_digest=version,
        compute_ms=0.0,
    )
