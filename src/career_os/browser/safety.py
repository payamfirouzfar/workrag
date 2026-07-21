from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class BlockerResult:
    blocked: bool
    reason: str
    blocker_type: str   # CAPTCHA | MFA | ANTI_BOT | PASSWORD | UNKNOWN


CAPTCHA_HINTS = [
    "captcha", "recaptcha", "hcaptcha", "turnstile", "are you human",
    "i'm not a robot", "verify you are human", "press and hold",
]
MFA_HINTS = ["two-factor", "2fa", "mfa", "verification code", "enter the code",
             "authenticator app", "one-time password", "otp"]
ANTIBOT_HINTS = ["checking your browser", "cloudflare", "datadome",
                 "akamai", "perimeterx", "kasada", "imperva"]


def detect_blocker(page_text: str) -> BlockerResult | None:
    t = (page_text or "").lower()
    for hint in CAPTCHA_HINTS:
        if hint in t:
            return BlockerResult(True, f"CAPTCHA detected ({hint})", "CAPTCHA")
    for hint in MFA_HINTS:
        if hint in t:
            return BlockerResult(True, f"MFA required ({hint})", "MFA")
    for hint in ANTIBOT_HINTS:
        if hint in t:
            return BlockerResult(True, f"Anti-bot ({hint})", "ANTI_BOT")
    if re.search(r"\b(password|passwd)\b\s*:", t):
        return BlockerResult(True, "Authentication form", "PASSWORD")
    return None
