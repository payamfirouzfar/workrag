from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.browser_application import BrowserApplicationAgent
from ..core.exceptions import ApprovalRequiredError
from ..db.models import Application, UserApproval
from ..db.session import get_session
from ..schemas.application import ApprovalDecision

router = APIRouter(prefix="/approval", tags=["approval"])


@router.post("/decide")
async def decide(
    decision: ApprovalDecision,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """This is the human-approval gate. Every application submission in this
    system passes through here first -- BrowserApplicationAgent.submit()
    hard-fails without a UserApproval row with decision == APPROVED."""
    application = await session.get(Application, uuid.UUID(decision.application_id))
    if application is None:
        raise HTTPException(404, "Application not found")

    approval = UserApproval(
        application_id=application.id,
        decision=decision.decision,
        notes=decision.notes,
    )
    session.add(approval)

    if decision.decision == "APPROVED":
        application.user_approved = True
        application.status = "APPROVED"
    elif decision.decision == "REJECTED":
        application.status = "REJECTED"

    await session.commit()
    await session.refresh(approval)

    return {"approval_id": str(approval.id), "application_status": application.status}


@router.post("/{application_id}/submit")
async def submit_application(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict:
    application = await session.get(Application, application_id)
    if application is None:
        raise HTTPException(404, "Application not found")

    if not application.user_approved:
        raise HTTPException(403, "Application has not been user-approved")

    agent = BrowserApplicationAgent(user_id=str(application.profile_id))
    try:
        # [MANUAL ACTION REQUIRED] agent.start(job.application_url) must run
        # before submit() in a real flow; omitted here since this route only
        # demonstrates the approval-gate enforcement, not live browser control.
        result = await agent.submit(application_id, uuid.uuid4())
    except ApprovalRequiredError as e:
        raise HTTPException(403, str(e))

    application.status = "SUBMITTED"
    await session.commit()
    return result
