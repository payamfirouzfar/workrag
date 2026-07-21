from datetime import datetime

from pydantic import BaseModel


class EmailEventOut(BaseModel):
    id: str
    sender: str
    subject: str
    category: str  # APPLICATION_CONFIRMATION | INTERVIEW_INVITE | REJECTION | PHISHING_SUSPECTED | OTHER
    linked_application_id: str | None = None
    phishing_score: float = 0.0
    received_at: datetime


class OAuthCallbackIn(BaseModel):
    code: str
    state: str | None = None
