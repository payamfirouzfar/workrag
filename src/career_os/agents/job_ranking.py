from __future__ import annotations

TIER_ORDER = {"TIER_1": 0, "TIER_2": 1, "TIER_3": 2, "TIER_4": 3, "DO_NOT_APPLY": 4}


class JobRankingAgent:
    """Sorts already-scored, already-verified jobs into the order presented
    to the user: tier first, then overall_score descending within a tier."""

    def rank(self, scored_jobs: list[dict]) -> list[dict]:
        return sorted(
            scored_jobs,
            key=lambda j: (TIER_ORDER.get(j["tier"], 99), -j["overall_score"]),
        )

    def top_n(self, scored_jobs: list[dict], n: int = 10) -> list[dict]:
        return [j for j in self.rank(scored_jobs) if j["tier"] != "DO_NOT_APPLY"][:n]
