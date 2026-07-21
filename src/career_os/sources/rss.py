from __future__ import annotations
import httpx, hashlib
from xml.etree import ElementTree
from .base import JobSourceAdapter, NormalizedJob
from .policy import SourceStatus


class RSSAdapter(JobSourceAdapter):
    """Generic RSS/Atom job-feed adapter — feeds are explicitly published
    for machine consumption, so this is always API_ALLOWED."""

    async def fetch(self, feed_url: str) -> list[NormalizedJob]:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(feed_url)
            r.raise_for_status()
            root = ElementTree.fromstring(r.text)

        out: list[NormalizedJob] = []
        items = root.findall(".//item") or root.findall(
            ".//{http://www.w3.org/2005/Atom}entry")
        for item in items:
            title = _find_text(item, "title")
            link = _find_text(item, "link") or (
                item.find("{http://www.w3.org/2005/Atom}link").attrib.get("href")
                if item.find("{http://www.w3.org/2005/Atom}link") is not None else ""
            )
            description = _find_text(item, "description") or _find_text(item, "summary") or ""
            canonical = hashlib.sha256(f"rss|{feed_url}|{link}".encode()).hexdigest()
            out.append(NormalizedJob(
                title=title or "",
                company=_find_text(item, "author") or "",
                location=None,
                remote_status=None,
                employment_type=None,
                description=description,
                requirements=[],
                preferred=[],
                application_url=link or "",
                source_url=link or "",
                source_type="rss",
                date_posted=None,
                deadline=None,
                source_policy_status=SourceStatus.API_ALLOWED.value,
                canonical_hash=canonical,
            ))
        return out


def _find_text(item, tag: str) -> str | None:
    el = item.find(tag)
    if el is None:
        el = item.find(f"{{http://www.w3.org/2005/Atom}}{tag}")
    return el.text if el is not None else None
