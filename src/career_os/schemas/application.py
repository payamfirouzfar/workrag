from datetime import datetime

from pydantic import BaseModel


class ApplicationAnswerOut(BaseModel):
    question: str
    answer: str | None
    needs_user_confirmation: bool = False


class ApplicationOut(BaseModel):
    id: str
    job_id: str
    status: str
    cv_version: str | None = None
    cover_letter_version: str | None = None
    submitted_at: datetime | None = None
    confirmation_received: bool = False
    user_approved: bool = False
    answers: list[ApplicationAnswerOut] = []


class ApprovalDecision(BaseModel):
    application_id: str
    decision: str  # APPROVED | REJECTED | EDITED
    notes: str | None = None
