from __future__ import annotations
import difflib

from ..sources.base import NormalizedJob


class JobDedupAgent:
    """Two layers: exact dedup on canonical_hash (same posting re-crawled),
    and fuzzy dedup on title+company (same role cross-posted to multiple
    boards, e.g. Greenhouse + a company's own site)."""

    def __init__(self, fuzzy_threshold: float = 0.92):
        self.fuzzy_threshold = fuzzy_threshold

    def dedupe(self, jobs: list[NormalizedJob]) -> list[NormalizedJob]:
        seen_hashes: set[str] = set()
        exact_unique: list[NormalizedJob] = []
        for job in jobs:
            if job.canonical_hash in seen_hashes:
                continue
            seen_hashes.add(job.canonical_hash)
            exact_unique.append(job)

        result: list[NormalizedJob] = []
        signatures: list[str] = []
        for job in exact_unique:
            sig = f"{job.title.lower().strip()}|{job.company.lower().strip()}"
            if any(difflib.SequenceMatcher(None, sig, existing).ratio() >= self.fuzzy_threshold
                   for existing in signatures):
                continue
            signatures.append(sig)
            result.append(job)
        return result
