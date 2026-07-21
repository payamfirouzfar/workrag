from __future__ import annotations
import httpx, hashlib
from .base import JobSourceAdapter, NormalizedJob
from .policy import SourceStatus


class WorkdayAdapter(JobSourceAdapter):
    """Workday CXS public job listing endpoint (PUBLIC_PAGE_ALLOWED — no
    documented public API contract, so this reads the same JSON the careers
    page itself fetches client-side rather than scraping rendered HTML)."""

    def __init__(self, tenant_host: str, site: str):
        # e.g. tenant_host="acme.wd1.myworkdayjobs.com", site="External"
        self.tenant_host = tenant_host
        self.site = site
        self.base = f"https://{tenant_host}/wday/cxs/{tenant_host.split('.')[0]}/{site}/jobs"

    async def fetch(self, limit: int = 50) -> list[NormalizedJob]:
        out: list[NormalizedJob] = []
        offset = 0
        async with httpx.AsyncClient(timeout=20) as c:
            while True:
                r = await c.post(self.base, json={"limit": limit, "offset": offset})
                r.raise_for_status()
                data = r.json()
                postings = data.get("jobPostings", [])
                if not postings:
                    break
                for p in postings:
                    ext_path = p.get("externalPath", "")
                    apply_url = f"https://{self.tenant_host}{ext_path}"
                    canonical = hashlib.sha256(
                        f"workday|{self.tenant_host}|{ext_path}".encode()
                    ).hexdigest()
                    out.append(NormalizedJob(
                        title=p.get("title", ""),
                        company=self.tenant_host.split(".")[0],
                        location=p.get("locationsText", ""),
                        remote_status=None,
                        employment_type=None,
                        description="",
                        requirements=[],
                        preferred=[],
                        application_url=apply_url,
                        source_url=apply_url,
                        source_type="workday",
                        date_posted=None,
                        deadline=None,
                        source_policy_status=SourceStatus.PUBLIC_PAGE_ALLOWED.value,
                        canonical_hash=canonical,
                    ))
                offset += limit
                if offset >= data.get("total", 0):
                    break
        return out
