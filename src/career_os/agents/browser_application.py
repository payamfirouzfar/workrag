from __future__ import annotations
import uuid

from ..browser.field_mapping import map_field, is_sensitive
from ..browser.safety import detect_blocker
from ..core.audit import audit_log
from ..core.exceptions import ApprovalRequiredError


def _resolve(path: str, profile: dict, generated_documents: dict):
    section, _, key = path.partition(".")
    if section == "documents":
        return generated_documents.get(key)
    return (profile.get(section) or {}).get(key)


class BrowserApplicationAgent:
    """Drives Playwright. Submits ONLY after explicit user approval."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self._session = None  # career_os.browser.session.BrowserSession

    async def start(self, url: str) -> dict:
        from ..browser.session import BrowserSession

        self._session = BrowserSession()
        await self._session.start()
        await self._session.goto(url)
        return {"url": url, "state": "APPLICATION_STARTED"}

    async def detect_and_fill(self, form_html: str, profile: dict,
                              generated_documents: dict) -> dict:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(form_html, "html.parser")
        filled: list[dict] = []
        sensitive: list[dict] = []
        for el in soup.find_all(["input", "textarea", "select"]):
            label = (el.get("name") or "") + " " + (el.get("id") or "") + " " + (el.get("placeholder") or "")
            label = label.strip()
            path = map_field(label)
            if not path:
                continue
            if is_sensitive(label):
                sensitive.append({"label": label, "field_path": path,
                                  "reason": "legally significant -- needs user input"})
                continue
            value = _resolve(path, profile, generated_documents)
            if value is not None:
                filled.append({"label": label, "field_path": path, "value_preview": str(value)[:80]})

        blocker = detect_blocker(form_html)

        await audit_log(
            user_id=self.user_id, action="FORM_FILLED",
            details={"filled_count": len(filled),
                     "sensitive_count": len(sensitive),
                     "blocker": blocker.blocker_type if blocker else None},
        )

        return {
            "filled": filled,
            "needs_user_input": sensitive,
            "blocker": blocker.__dict__ if blocker else None,
            "ready_for_review": not blocker and not sensitive,
        }

    async def submit(self, application_id: uuid.UUID, user_approval_id: uuid.UUID | None) -> dict:
        """Hard gate: there is no code path here that submits an
        application without a recorded UserApproval row. Callers must
        create that row (via the /approval API, which requires an explicit
        human decision) before this method will proceed."""
        if not user_approval_id:
            await audit_log(
                user_id=self.user_id, action="SUBMIT_BLOCKED_NO_APPROVAL",
                resource_type="application", resource_id=str(application_id),
            )
            raise ApprovalRequiredError(
                "Cannot submit without explicit user approval"
            )

        if self._session is None or self._session.page is None:
            raise RuntimeError("BrowserApplicationAgent.start() must be called first")

        # [MANUAL ACTION REQUIRED] Wire up the actual submit-button click and
        # post-submission confirmation-page scrape here, per ATS. Kept
        # abstract so the approval gate above is unit-testable without a
        # live browser.
        await self._session.page.click("button[type=submit]")

        await audit_log(
            user_id=self.user_id, action="APPLICATION_SUBMITTED",
            resource_type="application", resource_id=str(application_id),
            details={"user_approval_id": str(user_approval_id)},
        )

        return {"application_id": str(application_id), "state": "SUBMITTED"}
