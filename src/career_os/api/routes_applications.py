from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.application_strategy import ApplicationStrategyAgent
from ..agents.document_generation import DocumentGenerationAgent
from ..agents.profile_rag import ProfileRAGAgent
from ..core.exceptions import UnverifiedClaimError
from ..db.models import Application, Job, Profile
from ..db.session import get_session

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/{job_id}/prepare")
async def prepare_application(
    job_id: uuid.UUID,
    profile_id: uuid.UUID,
    match: dict,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Generates a verified cover letter draft and creates the Application
    row in DISCOVERED status. Nothing is submitted here -- that requires a
    separate, explicit approval via /approval."""
    job = await session.get(Job, job_id)
    profile_row = await session.get(Profile, profile_id)
    if job is None or profile_row is None:
        raise HTTPException(404, "Job or profile not found")

    strategy = ApplicationStrategyAgent().build_strategy(match, {
        "title": job.title, "company": job.company_name,
        "employment_type": job.employment_type,
    })

    rag_agent = ProfileRAGAgent(user_id=profile_row.user_id)
    doc_agent = DocumentGenerationAgent(profile_rag=rag_agent.rag)

    try:
        document = await doc_agent.require_verified_document(
            {"title": job.title, "company": job.company_name}, strategy,
        )
    except UnverifiedClaimError as e:
        raise HTTPException(422, str(e))

    application = Application(profile_id=profile_id, job_id=job_id, status="DRAFTED")
    session.add(application)
    await session.commit()
    await session.refresh(application)

    return {
        "application_id": str(application.id),
        "strategy": strategy,
        "cover_letter": document["cover_letter"],
        "unverified_claims": [v for v in document["verification"] if not v["verified"]],
    }


@router.get("/{application_id}")
async def get_application(application_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> dict:
    application = await session.get(Application, application_id)
    if application is None:
        raise HTTPException(404, "Application not found")
    return {
        "id": str(application.id),
        "status": application.status,
        "user_approved": application.user_approved,
        "submitted_at": application.submitted_at,
    }
