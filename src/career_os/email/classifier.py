from __future__ import annotations

from ..security.prompt_injection import sanitize_external_content

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "APPLICATION_CONFIRMATION": [
        "thank you for applying", "application received", "we have received your application",
    ],
    "INTERVIEW_INVITE": [
        "interview", "schedule a call", "phone screen", "meet with", "availability",
    ],
    "REJECTION": [
        "unfortunately", "not moving forward", "other candidates",
        "decided not to proceed", "position has been filled",
    ],
    "OFFER": ["offer letter", "pleased to offer", "job offer", "compensation package"],
}

PHISHING_KEYWORDS = [
    "wire transfer", "bitcoin", "crypto wallet", "send your bank",
    "processing fee", "western union", "gift card",
    "verify your identity by paying", "urgent payment required",
]


def classify_email(sender: str, subject: str, body: str) -> dict:
    """Rule-based first pass. [MANUAL ACTION REQUIRED] Swap in an LLM
    classifier for ambiguous cases once Gmail OAuth is wired up -- keep the
    sanitization step below regardless, since email bodies are the most
    common prompt-injection vector."""
    sanitized = sanitize_external_content(f"{subject}\n{body}", source=f"email:{sender}")
    text = sanitized["sanitized_text"].lower()

    phishing_hits = [kw for kw in PHISHING_KEYWORDS if kw in text]
    phishing_score = min(1.0, len(phishing_hits) * 0.3 + (0.5 if sanitized["is_injection"] else 0))

    category = "OTHER"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            category = cat
            break

    if phishing_score >= 0.5:
        category = "PHISHING_SUSPECTED"

    return {
        "category": category,
        "phishing_score": round(phishing_score, 2),
        "phishing_indicators": phishing_hits,
        "prompt_injection_detected": sanitized["is_injection"],
    }
