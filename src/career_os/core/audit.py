from __future__ import annotations

from ..db.models import AuditLog
from ..db.session import AsyncSessionLocal
from .logging import get_logger

logger = get_logger("audit")


async def audit_log(
    user_id: str,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict | None = None,
) -> None:
    """Every security-relevant action (profile ingestion, job verification,
    form fill, submission) MUST be recorded here. This is the accountability
    trail for a system that acts on the user's behalf."""
    logger.info("audit_event", user_id=user_id, action=action,
                resource_type=resource_type, resource_id=resource_id,
                details=details or {})
    try:
        async with AsyncSessionLocal() as session:
            session.add(AuditLog(
                user_id=user_id or None,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
            ))
            await session.commit()
    except Exception:
        # Audit logging must never crash the calling agent; the structured
        # log line above is the fallback record.
        logger.exception("audit_log_persist_failed", action=action)
