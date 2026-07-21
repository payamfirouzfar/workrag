from __future__ import annotations

from ..sources.ashby import AshbyAdapter
from ..sources.base import NormalizedJob
from ..sources.greenhouse import GreenhouseAdapter
from ..sources.lever import LeverAdapter
from ..sources.policy import SourcePolicy, SourceStatus
from ..sources.rss import RSSAdapter
from ..core.audit import audit_log


class JobDiscoveryAgent:
    """Pulls jobs from configured sources, filtering out anything the
    SourcePolicy classifies as NOT_ALLOWED before it ever reaches storage."""

    def __init__(self, user_id: str, respect_robots: bool = True):
        self.user_id = user_id
        self.policy = SourcePolicy(respect_robots=respect_robots)
        self.adapters = {
            "greenhouse": GreenhouseAdapter(),
            "lever": LeverAdapter(),
            "ashby": AshbyAdapter(),
            "rss": RSSAdapter(),
        }

    async def discover(self, source_type: str, identifier: str) -> list[NormalizedJob]:
        adapter = self.adapters.get(source_type)
        if adapter is None:
            raise ValueError(f"Unknown source_type: {source_type}")

        jobs = await adapter.fetch(identifier)

        allowed: list[NormalizedJob] = []
        for job in jobs:
            status = await self.policy.classify(job.application_url)
            if status == SourceStatus.NOT_ALLOWED:
                continue
            allowed.append(job)

        await audit_log(
            user_id=self.user_id,
            action="JOBS_DISCOVERED",
            resource_type="job_source",
            resource_id=identifier,
            details={"source_type": source_type, "fetched": len(jobs),
                     "allowed": len(allowed)},
        )
        return allowed
