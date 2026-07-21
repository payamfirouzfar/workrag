from __future__ import annotations


class ApplicationStrategyAgent:
    """Decides how to approach a given match: which gaps to address in the
    cover letter, whether to lead with research or industry experience,
    and what tone fits the company (inferred from the job description),
    all before any document text is generated."""

    def build_strategy(self, match: dict, job: dict) -> dict:
        gaps = match.get("gaps", [])
        reasons = match.get("reasons", [])

        emphasis = "research" if any("research" in r.lower() for r in reasons) else "experience"

        talking_points = list(reasons)
        if gaps:
            talking_points.append(
                f"Address gap(s) via transferable skills: {', '.join(gaps[:3])}"
            )

        return {
            "emphasis": emphasis,
            "talking_points": talking_points,
            "tone": "formal" if job.get("employment_type") == "full-time" else "conversational",
            "should_apply": match.get("tier") not in ("DO_NOT_APPLY",),
        }
