from __future__ import annotations
import httpx, hashlib
from .base import JobSourceAdapter, NormalizedJob
from .policy import SourceStatus


class GreenhouseAdapter(JobSourceAdapter):
    """Greenhouse Job Board API — public, documented, fully legal."""
    BASE = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"

    async def fetch(self, board: str) -> list[NormalizedJob]:
        url = self.BASE.format(board=board)
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(url)
            r.raise_for_status()
            data = r.json()

        out: list[NormalizedJob] = []
        for j in data.get("jobs", []):
            desc = j.get("content", "") or ""
            loc = (j.get("location") or {}).get("name", "")
            canonical = hashlib.sha256(
                f"greenhouse|{board}|{j['id']}".encode()
            ).hexdigest()
            out.append(NormalizedJob(
                title=j.get("title", ""),
                company=board,
                location=loc,
                remote_status=_infer_remote(loc),
                employment_type=None,
                description=desc,
                requirements=_split_requirements(desc),
                preferred=[],
                application_url=j.get("absolute_url", ""),
                source_url=j.get("absolute_url", ""),
                source_type="greenhouse",
                date_posted=j.get("updated_at"),
                deadline=None,
                source_policy_status=SourceStatus.API_ALLOWED.value,
                canonical_hash=canonical,
            ))
        return out


def _infer_remote(loc: str) -> str | None:
    if not loc:
        return None
    l = loc.lower()
    if "remote" in l:
        return "remote"
    if "hybrid" in l:
        return "hybrid"
    return "on-site"


def _split_requirements(desc: str) -> list[str]:
    import re
    m = re.search(r"(?:Requirements|Qualifications)[:\s]*(.*?)(?:\n[A-Z][a-z]+:|$)",
                  desc, re.DOTALL | re.IGNORECASE)
    if not m:
        return []
    return [b.strip("•-* \n") for b in m.group(1).split("\n") if b.strip()]
