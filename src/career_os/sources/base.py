from pydantic import BaseModel
from datetime import datetime


class NormalizedJob(BaseModel):
    title: str
    company: str
    location: str | None
    remote_status: str | None
    employment_type: str | None
    description: str
    requirements: list[str]
    preferred: list[str]
    application_url: str
    source_url: str
    source_type: str
    date_posted: datetime | None
    deadline: datetime | None
    source_policy_status: str
    canonical_hash: str


class JobSourceAdapter:
    async def fetch(self, *args, **kwargs) -> list[NormalizedJob]:
        raise NotImplementedError
