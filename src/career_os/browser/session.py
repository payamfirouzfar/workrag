from __future__ import annotations

from ..config import get_settings

SETTINGS = get_settings()


class BrowserSession:
    """Thin wrapper around a Playwright browser/context/page.

    [MANUAL ACTION REQUIRED] This is a scaffold: `start`/`close` wire up a
    real Playwright context using a persistent profile directory so login
    state (e.g. a job board account you're already signed into) survives
    between runs. Fill in real form-interaction methods per ATS as you test
    against live sites — the safety gates in `browser/safety.py` and
    `browser/field_mapping.py` are what must stay intact, not this class.
    """

    def __init__(self, headless: bool | None = None):
        self.headless = SETTINGS.browser_headless if headless is None else headless
        self._playwright = None
        self._browser = None
        self._context = None
        self.page = None

    async def start(self) -> None:
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=SETTINGS.browser_user_data_dir,
            headless=self.headless,
        )
        self.page = await self._context.new_page()

    async def goto(self, url: str) -> str:
        if self.page is None:
            raise RuntimeError("BrowserSession.start() must be called first")
        await self.page.goto(url, wait_until="domcontentloaded")
        return await self.page.content()

    async def close(self) -> None:
        if self._context:
            await self._context.close()
        if self._playwright:
            await self._playwright.stop()
