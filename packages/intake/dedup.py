"""Temporal deduplication with exact verification after MinHash candidates."""
from __future__ import annotations
import hashlib
import math
from collections import defaultdict
from typing import Any
from packages.core import Complaint, digest
from packages.intake import normalize, split_name

def shingles(text: str) -> frozenset[str]:
    words = normalize(text).split()
    return frozenset(" ".join(words[i:i+3]) for i in range(max(1, len(words)-2)))

def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    return len(a & b) / len(a | b) if a or b else 1.0

def temporal_dedup(rows: list[Complaint]) -> tuple[dict[str, list[Complaint]], list[dict[str, str]]]:
    from datasketch import MinHash, MinHashLSH
    # LSH is a retrieval optimization. The split audit independently checks candidates
    # using exact Jaccard and a lossless token-overlap inverted index.
    index = MinHashLSH(threshold=0.8, num_perm=128)
    retained: dict[str, Complaint] = {}
    lengths: dict[str, int] = {}
    inverted: dict[bytes, set[str]] = defaultdict(set)
    exact: dict[str, str] = {}
    output: dict[str, list[Complaint]] = defaultdict(list)
    drops = []
    for row in sorted(rows, key=lambda r: (r.received, int(r.odino))):
        split = split_name(row)
        if split is None: continue
        sig = shingles(row.feature.narrative)
        mh = MinHash(num_perm=128, seed=23)
        mh.update_batch([s.encode() for s in sorted(sig)])
        # Under one global token order, Jaccard >= .9 implies intersecting
        # prefixes of length |S|-ceil(.9*|S|)+1. Hash collisions only add
        # candidates: final similarity always uses original shingle strings.
        prefix = sorted(sig)[:len(sig)-math.ceil(.9*len(sig))+1]
        keys = [hashlib.blake2b(s.encode(),digest_size=8).digest() for s in prefix]
        candidates = set(index.query(mh))
        # Exact overlap candidates ensure MinHash false negatives cannot leak duplicates.
        for key in keys: candidates.update(inverted[key])
        match = exact.get(row.text_digest)
        if match is None:
            match = next((k for k in sorted(candidates)
                          if .9*len(sig) <= lengths[k] <= len(sig)/.9
                          and jaccard(sig, shingles(retained[k].feature.narrative)) >= 0.9), None)
        if match is not None:
            drops.append({"odino": row.odino, "reason": "duplicate", "earlier": match})
            continue
        output[split].append(row)
        retained[row.odino] = row
        lengths[row.odino] = len(sig)
        exact[row.text_digest] = row.odino
        index.insert(row.odino, mh)
        for key in keys: inverted[key].add(row.odino)
    return dict(output), drops

def registered_sample(rows: list[Complaint], count: int, seed: int = 23) -> list[str]:
    if count < 1 or len(rows) < count: raise ValueError("insufficient_sample_population")
    strata: dict[tuple[str, str], list[Complaint]] = defaultdict(list)
    for r in sorted(rows, key=lambda r: (r.received, r.odino)):
        strata[(r.received.isoformat()[:7], sorted(r.label.groups)[0])].append(r)
    # Proportional allocation with deterministic largest remainders.
    exact = {k: len(v) * count / len(rows) for k, v in strata.items()}
    allocation = {k: int(v) for k, v in exact.items()}
    order = sorted(strata, key=lambda k: (-(exact[k] - allocation[k]), k))
    for k in order[:count - sum(allocation.values())]: allocation[k] += 1
    chosen = []
    for k in sorted(strata):
        ordered = sorted(strata[k], key=lambda r: (digest([seed, r.odino]), r.odino))
        chosen.extend(r.odino for r in ordered[:allocation[k]])
    return sorted(chosen)
