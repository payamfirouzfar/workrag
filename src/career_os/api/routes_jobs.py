from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.job_discovery import JobDiscoveryAgent
from ..agents.job_dedup import JobDedupAgent
from ..agents.job_verification import JobVerificationAgent
from ..agents.job_matching import JobMatchingAgent
from ..agents.job_ranking import JobRankingAgent
from ..agents.profile_rag import ProfileRAGAgent
from ..db.models import Profile
from ..db.session import get_session
from ..schemas.profile import ProfileStructured

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/discover")
async def discover_jobs(
    profile_id: uuid.UUID,
    source_type: str,
    identifier: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    profile_row = await session.get(Profile, profile_id)
    if profile_row is None:
        raise HTTPException(404, "Profile not found")

    profile = ProfileStructured.model_validate(profile_row.structured)
    profile_rag = ProfileRAGAgent(user_id=profile_row.user_id)

    discovery = JobDiscoveryAgent(user_id=str(profile_row.user_id))
    jobs = await discovery.discover(source_type, identifier)
    deduped = JobDedupAgent().dedupe(jobs)

    verifier = JobVerificationAgent()
    matcher = JobMatchingAgent(profile=profile, profile_rag=profile_rag.rag)

    scored = []
    for job in deduped:
        job_dict = job.model_dump()
        verification = await verifier.verify(job_dict, user_id=str(profile_row.user_id))
        if not verification["verified"]:
            continue
        match = await matcher.score(job_dict)
        scored.append({"job": job_dict, **match})

    ranked = JobRankingAgent().top_n(scored, n=25)
    return {"count": len(ranked), "results": ranked}
