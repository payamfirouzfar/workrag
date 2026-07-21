import json

import pytest

from career_os.agents import profile_ingestion
from career_os.schemas.profile import Provenance

FAKE_LLM_JSON = json.dumps({
    "identity": {"name": "Jane Doe", "email": "jane@example.com"},
    "education": [{
        "institution": "MIT", "degree": "MSc", "field": "Computer Science",
        "start": "2019", "end": "2021",
    }],
    "skills": [
        {"name": "python", "category": "programming",
         "provenance": "CONFIRMED_FACT", "confidence": 1.0},
        {"name": "docker", "category": "tools",
         "provenance": "INFERRED_SKILL", "confidence": 0.6},
    ],
    "experience": [{
        "company": "Acme Corp", "role": "Software Engineer",
        "start": "2021", "end": "present", "description": "Built APIs in Python.",
    }],
    "projects": [], "research": [], "thesis": {}, "certifications": [],
    "languages": [],
    "career_preferences": {"desired_countries": ["Germany"]},
    "missing_information": ["phone number"],
})


class _FakeResponse:
    def __init__(self, content: str):
        self.content = content


class _FakeChain:
    async def ainvoke(self, _inputs):
        return _FakeResponse(FAKE_LLM_JSON)


class _FakePrompt:
    def __or__(self, _llm):
        return _FakeChain()


@pytest.fixture
def fake_cv(tmp_path):
    cv_path = tmp_path / "resume.txt"
    cv_path.write_text(
        "Jane Doe\nSoftware Engineer at Acme Corp\nMSc Computer Science, MIT\n"
        "Skills: Python, Docker\n",
        encoding="utf-8",
    )
    return cv_path


@pytest.mark.asyncio
async def test_ingest_resume_tags_provenance(fake_cv, monkeypatch):
    monkeypatch.setattr(profile_ingestion, "ChatOpenAI", lambda *a, **k: object())
    monkeypatch.setattr(
        profile_ingestion.ChatPromptTemplate, "from_messages",
        classmethod(lambda cls, _msgs: _FakePrompt()),
    )
    monkeypatch.setattr(profile_ingestion, "audit_log", _noop_audit)

    parsed = await profile_ingestion.ingest_resume(fake_cv, user_id="test-user")

    names = {s.name: s.provenance for s in parsed.structured.skills}
    assert names["python"] == Provenance.CONFIRMED_FACT
    assert names["docker"] == Provenance.INFERRED_SKILL
    assert "phone number" in parsed.structured.missing_information
    assert parsed.structured.experience[0].company == "Acme Corp"
    assert len(parsed.chunks) > 0


@pytest.mark.asyncio
async def test_ingest_resume_raises_on_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        await profile_ingestion.ingest_resume(tmp_path / "nope.txt", user_id="test-user")


async def _noop_audit(**kwargs):
    return None
