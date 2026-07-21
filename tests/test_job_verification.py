import httpx
import pytest
import respx

from career_os.security.url_safety import URLStatus, verify_job_url


@pytest.mark.asyncio
@respx.mock
async def test_verify_job_url_active_https():
    respx.get("https://boards.greenhouse.io/acme/jobs/123").mock(
        return_value=httpx.Response(200, text="<html>Job posting</html>")
    )
    result = await verify_job_url("https://boards.greenhouse.io/acme/jobs/123")
    assert result.status == URLStatus.ACTIVE
    assert result.https_valid is True


@pytest.mark.asyncio
@respx.mock
async def test_verify_job_url_not_found():
    respx.get("https://boards.greenhouse.io/acme/jobs/999").mock(
        return_value=httpx.Response(404)
    )
    result = await verify_job_url("https://boards.greenhouse.io/acme/jobs/999")
    assert result.status == URLStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_verify_job_url_flags_suspicious_tld():
    result = await verify_job_url("https://free-jobs.xyz/apply")
    assert "suspicious TLD" in " ".join(result.reasons)


@pytest.mark.asyncio
@respx.mock
async def test_verify_job_url_flags_phishing_keyword():
    respx.get("https://example.com/verify-account").mock(
        return_value=httpx.Response(200, text="ok")
    )
    result = await verify_job_url("https://example.com/verify-account")
    assert result.status == URLStatus.SUSPICIOUS
    assert "phishing keyword detected" in result.reasons
