from __future__ import annotations
import pathlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.profile_ingestion import ingest_resume
from ..agents.profile_rag import ProfileRAGAgent
from ..db.models import Profile, User
from ..db.session import get_session

router = APIRouter(prefix="/profile", tags=["profile"])

UPLOAD_DIR = pathlib.Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def _get_or_create_user(session: AsyncSession, email: str) -> User:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(email=email)
        session.add(user)
        await session.flush()
    return user


@router.post("/upload-cv")
async def upload_cv(
    file: UploadFile,
    email: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """[MANUAL ACTION REQUIRED] This is the entry point referenced in the
    README for uploading your resume. Accepts PDF or plain text."""
    if file.content_type not in ("application/pdf", "text/plain"):
        raise HTTPException(400, "Only PDF or plain-text resumes are supported")

    user = await _get_or_create_user(session, email)

    dest = UPLOAD_DIR / f"{user.id}_{file.filename}"
    content = await file.read()
    dest.write_bytes(content)

    parsed = await ingest_resume(dest, user_id=str(user.id))

    profile = Profile(
        user_id=user.id,
        raw_cv_path=str(dest),
        structured=parsed.structured.model_dump(mode="json"),
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)

    rag_agent = ProfileRAGAgent(user_id=user.id)
    indexed = await rag_agent.index_profile(parsed)

    return {
        "profile_id": str(profile.id),
        "missing_information": parsed.structured.missing_information,
        "skills_extracted": len(parsed.structured.skills),
        "chunks_indexed": indexed,
    }


@router.get("/{profile_id}")
async def get_profile(profile_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> dict:
    profile = await session.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(404, "Profile not found")
    return {"id": str(profile.id), "structured": profile.structured}
