from __future__ import annotations
import re

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(the\s+)?above",
    r"you\s+are\s+now\s+(?:a|an)\s+\w+",
    r"system\s*prompt",
    r"reveal\s+(your|the)\s+(?:system|initial)\s+prompt",
    r"new\s+instructions?\s*:",
    r"print\s+(your|the)\s+instructions",
    r"jailbreak",
    r"</?\s*(?:system|prompt|developer)\s*>",
    r"do\s+not\s+follow\s+(?:your|the)\s+rules",
]

COMPILED = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def detect_prompt_injection(text: str) -> dict:
    findings = [p.pattern for p in COMPILED if p.search(text or "")]
    return {
        "is_injection": bool(findings),
        "patterns_matched": findings,
        "severity": "high" if findings else "none",
        "action": "BLOCK_AND_REPORT" if findings else "PROCEED",
    }


def sanitize_external_content(text: str, source: str) -> dict:
    """Every web page, email, PDF, job description passes through here."""
    result = detect_prompt_injection(text)
    if result["is_injection"]:
        cleaned = text
        for p in COMPILED:
            cleaned = p.sub("[REDACTED-PROMPT-INJECTION]", cleaned)
        return {
            "safe": False,
            "sanitized_text": cleaned,
            "original_blocked": True,
            "source": source,
            **result,
        }
    return {"safe": True, "sanitized_text": text, "source": source, **result}
