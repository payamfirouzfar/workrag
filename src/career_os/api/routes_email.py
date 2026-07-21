from __future__ import annotations
import secrets

from fastapi import APIRouter, HTTPException

from ..email.classifier import classify_email
from ..email.oauth import build_authorization_url, exchange_code_for_tokens
from ..schemas.email import OAuthCallbackIn

router = APIRouter(prefix="/email", tags=["email"])


@router.get("/oauth/start")
async def oauth_start() -> dict:
    state = secrets.token_urlsafe(24)
    return {"authorization_url": build_authorization_url(state), "state": state}


@router.post("/oauth/callback")
async def oauth_callback(payload: OAuthCallbackIn) -> dict:
    """[MANUAL ACTION REQUIRED] Store the resulting refresh_token in an OS
    keychain or secrets manager, not in application state."""
    try:
        tokens = await exchange_code_for_tokens(payload.code)
    except Exception as e:
        raise HTTPException(400, f"OAuth exchange failed: {e}")
    return {"connected": True, "scope": tokens.get("scope", "")}


@router.post("/classify")
async def classify(sender: str, subject: str, body: str) -> dict:
    return classify_email(sender, subject, body)
