"""Word and character TF-IDF floor with independent development calibration."""

from __future__ import annotations

import time
from typing import Any

from packages.core import Complaint, Feature, Prediction, digest


class Floor:
    def __init__(self) -> None:
        self.groups: list[str] = []
        self.vectorizer: Any = None
        self.heads: list[Any] = []
        self.calibrators: list[Any] = []
        self.version = ""
        self.c = 0.0

    def fit(self, train: list[Complaint], development: list[Complaint]) -> dict[str, Any]:
        import numpy as np
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import log_loss
        from sklearn.pipeline import FeatureUnion

        if not train or not development:
            raise ValueError("missing_training_data")
        self.groups = sorted({g for r in train for g in r.label.groups})
        if "OTHER" not in self.groups:
            self.groups.append("OTHER")
        self.vectorizer = FeatureUnion(
            [
                (
                    "word",
                    TfidfVectorizer(
                        ngram_range=(1, 2), min_df=2, max_features=60000, sublinear_tf=True
                    ),
                ),
                (
                    "character",
                    TfidfVectorizer(
                        analyzer="char_wb",
                        ngram_range=(3, 5),
                        min_df=2,
                        max_features=80000,
                        sublinear_tf=True,
                    ),
                ),
            ]
        )
        x = self.vectorizer.fit_transform([r.feature.narrative for r in train])
        xd = self.vectorizer.transform([r.feature.narrative for r in development])
        y = np.array(
            [[int(g in r.label.groups) for g in self.groups] + [int(r.label.safety)] for r in train]
        )
        yd = np.array(
            [
                [int(g in r.label.groups) for g in self.groups] + [int(r.label.safety)]
                for r in development
            ]
        )
        candidates = []
        for c in (0.1, 1.0, 10.0):
            heads, loss = [], 0.0
            for j in range(y.shape[1]):
                if len(set(y[:, j])) < 2:
                    heads.append(float(y[:, j].mean()))
                    probability = np.full(len(development), heads[-1])
                else:
                    head = LogisticRegression(
                        C=c, max_iter=300, solver="liblinear", random_state=23
                    )
                    head.fit(x, y[:, j])
                    heads.append(head)
                    probability = head.predict_proba(xd)[:, 1]
                loss += float(log_loss(yd[:, j], probability, labels=[0, 1]))
            candidates.append((loss, c, heads))
        _, self.c, self.heads = min(candidates, key=lambda v: (v[0], v[1]))
        self.calibrators = []
        for j, head in enumerate(self.heads):
            if isinstance(head, float) or len(set(yd[:, j])) < 2:
                self.calibrators.append(None)
            else:
                cal = LogisticRegression(C=1e6, solver="lbfgs")
                cal.fit(head.decision_function(xd).reshape(-1, 1), yd[:, j])
                self.calibrators.append(cal)
        self.version = digest(
            {
                "arm": "floor",
                "c": self.c,
                "groups": self.groups,
                "train": [r.text_digest for r in train],
                "development": [r.text_digest for r in development],
            }
        )
        return {
            "arm": "floor",
            "training_count": len(train),
            "development_count": len(development),
            "c": self.c,
            "version": self.version,
            "calibration": "Platt on development",
            "candidate_losses": [{"c": c, "loss": loss} for loss, c, _ in candidates],
        }

    def predict(self, features: list[Feature]) -> list[Prediction]:
        import numpy as np

        if self.vectorizer is None or not self.version:
            raise ValueError("floor_not_fitted")
        start = time.perf_counter()
        x = self.vectorizer.transform([f.narrative for f in features])
        columns = []
        for head, cal in zip(self.heads, self.calibrators, strict=True):
            if isinstance(head, float):
                column = np.full(len(features), head)
            elif cal is not None:
                column = cal.predict_proba(head.decision_function(x).reshape(-1, 1))[:, 1]
            else:
                column = head.predict_proba(x)[:, 1]
            columns.append(column)
        values = np.column_stack(columns)
        ms = (time.perf_counter() - start) * 1000 / max(1, len(features))
        return [
            Prediction(
                scores={g: float(v[i]) for i, g in enumerate(self.groups)},
                safety_probability=float(v[-1]),
                arm="floor",
                version_digest=self.version,
                compute_ms=ms,
            )
            for v in values
        ]
