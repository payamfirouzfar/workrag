from __future__ import annotations
import httpx
from urllib.parse import urlparse
from dataclasses import dataclass
from enum import Enum


class URLStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REDIRECTED = "REDIRECTED"
    EXPIRED = "EXPIRED"
    NOT_FOUND = "NOT_FOUND"
    SUSPICIOUS = "SUSPICIOUS"
    REQUIRES_AUTHENTICATION = "REQUIRES_AUTHENTICATION"


SUSPICIOUS_TLDS = {".zip", ".mov", ".xyz", ".top", ".click", ".country"}
PHISHING_KEYWORDS = {"verify-account", "login-secure", "wallet-connect",
                     "crypto-reward", "free-gift"}


@dataclass
class VerificationResult:
    url: str
    status: URLStatus
    final_url: str
    redirects: list[str]
    https_valid: bool
    reasons: list[str]


async def verify_job_url(url: str) -> VerificationResult:
    reasons: list[str] = []
    redirects: list[str] = []
    parsed = urlparse(url)
    https_valid = parsed.scheme == "https"

    if parsed.scheme != "https":
        reasons.append("non-HTTPS URL")

    host = parsed.netloc.lower()
    if any(host.endswith(t) for t in SUSPICIOUS_TLDS):
        reasons.append(f"suspicious TLD: {host}")
    if any(kw in url.lower() for kw in PHISHING_KEYWORDS):
        reasons.append("phishing keyword detected")

    final = url
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
            r = await c.get(url)
            redirects = [str(h.url) for h in r.history]
            final = str(r.url)
            if r.status_code == 404:
                status = URLStatus.NOT_FOUND
            elif r.status_code in (401, 403):
                status = URLStatus.REQUIRES_AUTHENTICATION
            elif r.status_code >= 400:
                status = URLStatus.EXPIRED
            elif r.history and urlparse(final).netloc != host:
                if any(urlparse(rd).netloc.endswith(t) for t in SUSPICIOUS_TLDS
                       for rd in redirects):
                    status = URLStatus.SUSPICIOUS
                    reasons.append("redirects to suspicious domain")
                else:
                    status = URLStatus.REDIRECTED
            else:
                status = URLStatus.ACTIVE
    except Exception as e:
        status = URLStatus.SUSPICIOUS
        reasons.append(f"request failed: {e!s}")

    if reasons and status == URLStatus.ACTIVE:
        status = URLStatus.SUSPICIOUS

    return VerificationResult(
        url=url, status=status, final_url=final,
        redirects=redirects, https_valid=https_valid, reasons=reasons,
    )
