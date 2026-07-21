from __future__ import annotations

from ..schemas.profile import ProfileStructured, Provenance
from ..rag.retriever import ProfileRAG
from ..llm.factory import get_embeddings_client

WEIGHTS = {
    "technical": 0.30, "experience": 0.20, "education": 0.10,
    "project": 0.10, "research": 0.10, "location": 0.05,
    "visa": 0.05, "career_goal": 0.05, "feasibility": 0.05,
}


class JobMatchingAgent:
    def __init__(self, profile: ProfileStructured, profile_rag: ProfileRAG):
        self.profile = profile
        self.rag = profile_rag
        self.embeddings = get_embeddings_client()

    async def score(self, job: dict) -> dict:
        confirmed_skills = {s.name.lower() for s in self.profile.skills
                            if s.provenance == Provenance.CONFIRMED_FACT}
        inferred_skills = {s.name.lower() for s in self.profile.skills
                           if s.provenance == Provenance.INFERRED_SKILL}
        all_skills = confirmed_skills | inferred_skills

        req_text = " ".join(job.get("requirements", []) or []).lower()
        desc_text = (job.get("description") or "").lower()
        corpus = f"{req_text} {desc_text}"

        tech_hits, tech_gaps = [], []
        for s in all_skills:
            (tech_hits if s in corpus else tech_gaps).append(s)
        tech_score = (len(tech_hits) / max(1, len(all_skills))) * 100

        evidence = await self.rag.retrieve(
            f"experience relevant to: {job['title']} at {job['company']}",
            k=4, provenance_filter=["CONFIRMED_FACT", "INFERRED_SKILL"],
        )
        sem_score = min(100, sum(e["score"] * 25 for e in evidence[:4]))

        technical_match = 0.6 * tech_score + 0.4 * sem_score

        years = max(0, len(self.profile.experience))
        exp_match = min(100, years * 25)

        edu_match = 100 if self.profile.education else 30

        proj_ev = await self.rag.retrieve(
            f"projects or research related to {job['title']}", k=3)
        project_match = min(100, sum(e["score"] * 33 for e in proj_ev[:3]))
        research_match = project_match

        loc_match = 100
        prefs = self.profile.career_preferences
        if job.get("location") and prefs.desired_countries:
            loc_match = 100 if any(c.lower() in (job["location"] or "").lower()
                                   for c in prefs.desired_countries) else 40

        visa_match = 80
        career_match = 80
        feasibility = 90

        component = {
            "technical": technical_match, "experience": exp_match,
            "education": edu_match, "project": project_match,
            "research": research_match, "location": loc_match,
            "visa": visa_match, "career_goal": career_match,
            "feasibility": feasibility,
        }
        overall = sum(component[k] * WEIGHTS[k] for k in WEIGHTS)

        reasons = []
        if technical_match > 75: reasons.append("Strong technical alignment")
        if project_match > 60:  reasons.append("Relevant projects/research")
        if edu_match == 100:    reasons.append("Education requirement satisfied")
        if loc_match == 100:    reasons.append("Location matches preferences")
        gaps = tech_gaps[:5]

        tier = ("TIER_1" if overall >= 85 else
                "TIER_2" if overall >= 70 else
                "TIER_3" if overall >= 55 else
                "TIER_4" if overall >= 40 else "DO_NOT_APPLY")

        return {
            "overall_score": round(overall, 1),
            "component_scores": {k: round(v, 1) for k, v in component.items()},
            "reasons": reasons,
            "gaps": gaps,
            "tier": tier,
            "confidence": round(min(1.0, len(evidence) / 4 + 0.5), 2),
        }
