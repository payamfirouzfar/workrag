from datetime import datetime

from pydantic import BaseModel


class JobIn(BaseModel):
    title: str
    company: str
    location: str | None = None
    remote_status: str | None = None
    employment_type: str | None = None
    description: str
    requirements: list[str] = []
    preferred: list[str] = []
    application_url: str
    source_url: str
    source_type: str
    date_posted: datetime | None = None
    deadline: datetime | None = None


class JobOut(JobIn):
    id: str
    url_status: str = "ACTIVE"
    created_at: datetime


class JobMatchOut(BaseModel):
    job_id: str
    overall_score: float
    component_scores: dict
    reasons: list[str]
    gaps: list[str]
    tier: str
    confidence: float = 1.0
