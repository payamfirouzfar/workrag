from __future__ import annotations
from ..security.url_safety import verify_job_url, URLStatus
from ..security.prompt_injection import sanitize_external_content
from ..core.audit import audit_log


class JobVerificationAgent:
    async def verify(self, job: dict, user_id: str) -> dict:
        url_result = await verify_job_url(job["application_url"])

        sanitization = sanitize_external_content(
            job.get("description", ""), source=job["application_url"])

        desc_lower = (job.get("description") or "").lower()
        red_flags = []
        for kw in ["wire transfer", "bitcoin", "crypto wallet",
                   "send your bank", "processing fee", "western union",
                   "gift card", "verify your identity by paying"]:
            if kw in desc_lower:
                red_flags.append(kw)

        suspicious = (
            url_result.status in (URLStatus.SUSPICIOUS, URLStatus.NOT_FOUND)
            or sanitization["is_injection"]
            or bool(red_flags)
        )

        await audit_log(
            user_id=user_id,
            action="JOB_VERIFIED" if not suspicious else "JOB_FLAGGED",
            resource_type="job",
            resource_id=job.get("application_url", ""),
            details={
                "url_status": url_result.status.value,
                "redirects": url_result.redirects,
                "https_valid": url_result.https_valid,
                "prompt_injection": sanitization["is_injection"],
                "red_flags": red_flags,
            },
        )

        return {
            "verified": not suspicious,
            "url_status": url_result.status.value,
            "final_url": url_result.final_url,
            "redirects": url_result.redirects,
            "https_valid": url_result.https_valid,
            "prompt_injection": sanitization["is_injection"],
            "red_flags": red_flags,
            "reasons": url_result.reasons,
            "decision": "APPROVE" if not suspicious else "FLAG_FOR_USER_REVIEW",
        }
