from __future__ import annotations
import re

FIELD_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"first\s*name", re.I), "identity.first_name"),
    (re.compile(r"last\s*name|surname|family\s*name", re.I), "identity.last_name"),
    (re.compile(r"full\s*name", re.I), "identity.full_name"),
    (re.compile(r"e-?mail", re.I), "identity.email"),
    (re.compile(r"phone", re.I), "identity.phone"),
    (re.compile(r"linkedin", re.I), "identity.linkedin"),
    (re.compile(r"github", re.I), "identity.github"),
    (re.compile(r"website|portfolio|personal\s*site", re.I), "identity.website"),
    (re.compile(r"highest\s*degree|degree\s*obtained", re.I), "education.highest_degree"),
    (re.compile(r"university|school|institution", re.I), "education.institution"),
    (re.compile(r"authorized\s*to\s*work|legally\s*authorized", re.I),
     "work_authorization.legally_authorized"),
    (re.compile(r"require\s*sponsorship|need\s*sponsorship|future\s*sponsorship", re.I),
     "work_authorization.requires_sponsorship"),
    (re.compile(r"relocat", re.I), "preferences.relocation"),
    (re.compile(r"salary|compensation|expectation", re.I), "preferences.salary"),
    (re.compile(r"start\s*date|earliest\s*start", re.I), "preferences.start_date"),
    (re.compile(r"resume|cv|curriculum", re.I), "documents.cv"),
    (re.compile(r"cover\s*letter", re.I), "documents.cover_letter"),
]

# Questions that ALWAYS require explicit user confirmation
SENSITIVE_QUESTION_PATTERNS = [
    r"require\s+sponsorship",
    r"legally\s+authorized",
    r"work\s+authorization",
    r"security\s+clearance",
    r"criminal\s+history",
    r"disability",
    r"veteran",
    r"race|ethnicity|gender",
    r"salary|compensation",
]


def map_field(label: str) -> str | None:
    for pat, path in FIELD_PATTERNS:
        if pat.search(label):
            return path
    return None


def is_sensitive(label: str) -> bool:
    return any(re.search(p, label, re.I) for p in SENSITIVE_QUESTION_PATTERNS)
