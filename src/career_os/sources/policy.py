from __future__ import annotations
from enum import Enum
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import httpx


class SourceStatus(str, Enum):
    API_ALLOWED = "API_ALLOWED"
    PUBLIC_PAGE_ALLOWED = "PUBLIC_PAGE_ALLOWED"
    AUTHORIZED_BROWSER_AUTOMATION = "AUTHORIZED_BROWSER_AUTOMATION"
    USER_ASSISTED_ONLY = "USER_ASSISTED_ONLY"
    NOT_ALLOWED = "NOT_ALLOWED"


KNOWN_ATS_DOMAINS = {
    "boards.greenhouse.io": SourceStatus.API_ALLOWED,
    "job-boards.greenhouse.io": SourceStatus.API_ALLOWED,
    "jobs.lever.co": SourceStatus.API_ALLOWED,
    "api.greenhouse.io": SourceStatus.API_ALLOWED,
    "workday.com": SourceStatus.PUBLIC_PAGE_ALLOWED,
    "ashbyhq.com": SourceStatus.API_ALLOWED,
    "myworkdayjobs.com": SourceStatus.PUBLIC_PAGE_ALLOWED,
}

BLOCKED_DOMAINS: set[str] = {
    # sites that explicitly prohibit scraping in their ToS
}


class SourcePolicy:
    def __init__(self, respect_robots: bool = True):
        self.respect_robots = respect_robots
        self._robots_cache: dict[str, RobotFileParser] = {}

    async def classify(self, url: str) -> SourceStatus:
        host = urlparse(url).netloc.lower()

        if host in BLOCKED_DOMAINS:
            return SourceStatus.NOT_ALLOWED
        if host in KNOWN_ATS_DOMAINS:
            return KNOWN_ATS_DOMAINS[host]

        if self.respect_robots:
            allowed = await self._robots_allows(url)
            if not allowed:
                return SourceStatus.NOT_ALLOWED

        if "/api/" in url or url.endswith(".rss") or url.endswith(".xml"):
            return SourceStatus.API_ALLOWED
        return SourceStatus.PUBLIC_PAGE_ALLOWED

    async def _robots_allows(self, url: str) -> bool:
        host = urlparse(url).netloc
        if host not in self._robots_cache:
            rp = RobotFileParser()
            robots_url = f"https://{host}/robots.txt"
            try:
                async with httpx.AsyncClient(timeout=10) as c:
                    r = await c.get(robots_url)
                    if r.status_code == 200:
                        rp.parse(r.text.splitlines())
                    else:
                        rp.parse([])
            except Exception:
                rp.parse([])
            self._robots_cache[host] = rp
        return self._robots_cache[host].can_fetch("AI-Career-OS", url)
