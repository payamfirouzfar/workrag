import pytest

from career_os.agents.job_matching import JobMatchingAgent


@pytest.mark.asyncio
async def test_strong_match_scores_high(sample_profile, fake_profile_rag, monkeypatch):
    monkeypatch.setattr(
        "career_os.agents.job_matching.get_embeddings_client",
        lambda *a, **k: object(),
    )
    agent = JobMatchingAgent(profile=sample_profile, profile_rag=fake_profile_rag)

    job = {
        "title": "Machine Learning Engineer",
        "company": "Acme Corp",
        "location": "Berlin, Germany",
        "description": "We need someone with python and pytorch experience.",
        "requirements": ["python", "pytorch", "sql"],
    }
    result = await agent.score(job)

    assert result["overall_score"] > 50
    assert result["tier"] in ("TIER_1", "TIER_2", "TIER_3")
    assert "location" in result["component_scores"]
    assert result["component_scores"]["location"] == 100  # Germany matches preference


@pytest.mark.asyncio
async def test_missing_skills_produce_gaps(sample_profile, fake_profile_rag, monkeypatch):
    monkeypatch.setattr(
        "career_os.agents.job_matching.get_embeddings_client",
        lambda *a, **k: object(),
    )
    agent = JobMatchingAgent(profile=sample_profile, profile_rag=fake_profile_rag)

    job = {
        "title": "Kubernetes Platform Engineer",
        "company": "Other Co",
        "location": "Remote",
        "description": "Deep Kubernetes, Terraform, and Go experience required.",
        "requirements": ["kubernetes", "terraform", "go"],
    }
    result = await agent.score(job)

    assert set(result["gaps"]) & {"python", "pytorch", "sql"}
