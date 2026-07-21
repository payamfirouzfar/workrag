import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://career:career_dev@localhost:5432/career_os")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

import pytest

from career_os.schemas.profile import (
    CareerPreferences, EducationItem, ExperienceItem, ProfileStructured,
    Provenance, SkillItem,
)


@pytest.fixture
def sample_profile() -> ProfileStructured:
    return ProfileStructured(
        identity={"name": "Test Candidate", "email": "test@example.com"},
        education=[EducationItem(institution="Test University", degree="MSc",
                                 field="Computer Science", start="2020", end="2022")],
        skills=[
            SkillItem(name="python", category="programming",
                     provenance=Provenance.CONFIRMED_FACT, confidence=1.0),
            SkillItem(name="pytorch", category="machine_learning",
                     provenance=Provenance.CONFIRMED_FACT, confidence=1.0),
            SkillItem(name="sql", category="databases",
                     provenance=Provenance.INFERRED_SKILL, confidence=0.7),
        ],
        experience=[ExperienceItem(company="Acme Corp", role="ML Engineer",
                                   start="2022", end="present",
                                   description="Built recommendation systems.")],
        career_preferences=CareerPreferences(desired_countries=["Germany"]),
    )


class FakeProfileRAG:
    """In-memory stand-in for ProfileRAG so agent tests don't need a live
    Postgres/pgvector instance or an OpenAI API key."""

    def __init__(self, hits: list[dict] | None = None):
        self._hits = hits or []

    async def retrieve(self, query: str, k: int = 6, provenance_filter=None) -> list[dict]:
        return self._hits[:k]

    async def verify_claim(self, claim: str) -> dict:
        if self._hits:
            return {"verified": True, "evidence": self._hits[0], "confidence": self._hits[0]["score"]}
        return {"verified": False, "reason": "no supporting evidence in profile",
                "missing_information": [claim]}


@pytest.fixture
def fake_profile_rag() -> FakeProfileRAG:
    return FakeProfileRAG(hits=[
        {"text": "Skill: python (category=programming, provenance=CONFIRMED_FACT, confidence=1.0)",
         "score": 0.9, "source": "cv.pdf", "doc_type": "skill",
         "provenance": "CONFIRMED_FACT", "confidence": 1.0},
        {"text": "Experience: ML Engineer @ Acme Corp (2022-present). Built recommendation systems.",
         "score": 0.85, "source": "cv.pdf", "doc_type": "experience",
         "provenance": "CONFIRMED_FACT", "confidence": 1.0},
    ])
