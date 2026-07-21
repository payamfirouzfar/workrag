from __future__ import annotations
import httpx, hashlib
from .base import JobSourceAdapter, NormalizedJob
from .policy import SourceStatus


class LeverAdapter(JobSourceAdapter):
    """Lever Postings API — public, documented, fully legal."""
    BASE = "https://api.lever.co/v0/postings/{site}?mode=json"

    async def fetch(self, site: str) -> list[NormalizedJob]:
        url = self.BASE.format(site=site)
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(url)
            r.raise_for_status()
            postings = r.json()

        out: list[NormalizedJob] = []
        for p in postings:
            desc_html = p.get("descriptionPlain") or p.get("description", "")
            categories = p.get("categories", {}) or {}
            location = categories.get("location", "")
            canonical = hashlib.sha256(
                f"lever|{site}|{p.get('id', '')}".encode()
            ).hexdigest()
            lists = p.get("lists", []) or []
            requirements = [
                item.get("text", "")
                for section in lists
                for item in section.get("content", "").split("\n")
                if item
            ] if lists else []
            out.append(NormalizedJob(
                title=p.get("text", ""),
                company=site,
                location=location,
                remote_status="remote" if "remote" in location.lower() else None,
                employment_type=categories.get("commitment"),
                description=desc_html,
                requirements=requirements,
                preferred=[],
                application_url=p.get("applyUrl") or p.get("hostedUrl", ""),
                source_url=p.get("hostedUrl", ""),
                source_type="lever",
                date_posted=None,
                deadline=None,
                source_policy_status=SourceStatus.API_ALLOWED.value,
                canonical_hash=canonical,
            ))
        return out
