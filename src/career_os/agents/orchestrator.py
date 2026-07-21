from __future__ import annotations
import asyncio
import sys

from ..core.logging import configure_logging, get_logger
from ..config import get_settings

SETTINGS = get_settings()
configure_logging(SETTINGS.app_env)
logger = get_logger("orchestrator")


class Orchestrator:
    """Coordinates the agent pipeline:
    discovery -> extraction -> dedup -> matching -> verification -> ranking
    -> strategy -> document generation -> (human approval gate) -> browser
    application.

    [MANUAL ACTION REQUIRED] This wires the pipeline steps together for a
    single user/profile; a full build would drive this from a task queue
    (Redis/RQ or Celery) reading Job/Profile rows rather than the in-memory
    demonstration below.
    """

    async def run_discovery_to_matching(self, user_id: str, profile, profile_rag,
                                        source_type: str, identifier: str) -> list[dict]:
        from .job_discovery import JobDiscoveryAgent
        from .job_dedup import JobDedupAgent
        from .job_matching import JobMatchingAgent
        from .job_verification import JobVerificationAgent
        from .job_ranking import JobRankingAgent

        discovery = JobDiscoveryAgent(user_id=user_id)
        jobs = await discovery.discover(source_type, identifier)

        deduped = JobDedupAgent().dedupe(jobs)

        verifier = JobVerificationAgent()
        matcher = JobMatchingAgent(profile=profile, profile_rag=profile_rag)

        results = []
        for job in deduped:
            job_dict = job.model_dump()
            verification = await verifier.verify(job_dict, user_id=user_id)
            if not verification["verified"]:
                continue
            match = await matcher.score(job_dict)
            results.append({"job": job_dict, "match": match, "verification": verification})

        ranked = JobRankingAgent().top_n(
            [{"job": r["job"], **r["match"]} for r in results], n=25
        )
        return ranked


async def _worker_loop() -> None:
    logger.info("worker_started")
    # [MANUAL ACTION REQUIRED] Replace with a real queue consumer
    # (e.g. Redis Streams / RQ) that pulls pending discovery/matching jobs.
    while True:
        await asyncio.sleep(3600)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        asyncio.run(_worker_loop())
    else:
        print("Usage: python -m career_os.agents.orchestrator worker")


if __name__ == "__main__":
    main()
