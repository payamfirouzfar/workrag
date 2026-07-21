from __future__ import annotations

import httpx

from ..config import get_settings

SETTINGS = get_settings()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


def build_authorization_url(state: str) -> str:
    params = {
        "client_id": SETTINGS.gmail_client_id,
        "redirect_uri": SETTINGS.gmail_redirect_uri,
        "response_type": "code",
        "scope": GMAIL_READONLY_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def exchange_code_for_tokens(code: str) -> dict:
    """[MANUAL ACTION REQUIRED] Register an OAuth client in Google Cloud
    Console, set GMAIL_CLIENT_ID/SECRET, and store the returned
    `refresh_token` in an OS keychain or secrets manager -- never in the
    application database."""
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(GOOGLE_TOKEN_URL, data={
            "client_id": SETTINGS.gmail_client_id,
            "client_secret": SETTINGS.gmail_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": SETTINGS.gmail_redirect_uri,
        })
        r.raise_for_status()
        return r.json()


async def refresh_access_token(refresh_token: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(GOOGLE_TOKEN_URL, data={
            "client_id": SETTINGS.gmail_client_id,
            "client_secret": SETTINGS.gmail_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        })
        r.raise_for_status()
        return r.json()
