from __future__ import annotations
import httpx, hashlib
from .base import JobSourceAdapter, NormalizedJob
from .policy import SourceStatus


class AshbyAdapter(JobSourceAdapter):
    """Ashby public job board API — public, documented, fully legal."""
    BASE = "https://api.ashbyhq.com/posting-api/job-board/{board}"

    async def fetch(self, board: str) -> list[NormalizedJob]:
        url = self.BASE.format(board=board)
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(url, params={"includeCompensation": "true"})
            r.raise_for_status()
            data = r.json()

        out: list[NormalizedJob] = []
        for j in data.get("jobs", []):
            desc = j.get("descriptionPlain") or j.get("descriptionHtml", "") or ""
            location = j.get("location", "")
            canonical = hashlib.sha256(
                f"ashby|{board}|{j.get('id', '')}".encode()
            ).hexdigest()
            out.append(NormalizedJob(
                title=j.get("title", ""),
                company=board,
                location=location,
                remote_status="remote" if j.get("isRemote") else None,
                employment_type=j.get("employmentType"),
                description=desc,
                requirements=[],
                preferred=[],
                application_url=j.get("applyUrl") or j.get("jobUrl", ""),
                source_url=j.get("jobUrl", ""),
                source_type="ashby",
                date_posted=j.get("publishedAt"),
                deadline=None,
                source_policy_status=SourceStatus.API_ALLOWED.value,
                canonical_hash=canonical,
            ))
        return out
