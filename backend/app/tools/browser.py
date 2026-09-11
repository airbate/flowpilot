"""Playwright executor for the browser subset of the step DSL.

Playwright ships as a library only — browsers must be installed once:
    pip install playwright && playwright install chromium
"""

from pathlib import Path
from uuid import uuid4

from app.agent.schemas import ActionKind, FlowStep


class BrowserTool:
    """Headless Chromium driven step-by-step; every step returns structured data."""

    def __init__(self) -> None:
        self.started = False

    async def ensure_started(self) -> None:
        if self.started:
            return
        from playwright.async_api import async_playwright

        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=True)
        self._page = await self._browser.new_page()
        self.started = True

    async def run_step(self, step: FlowStep) -> dict:
        if not self.started:
            await self.ensure_started()
        page = self._page
        if step.action is ActionKind.NAVIGATE:
            await page.goto(step.url or "", wait_until="domcontentloaded")
            return {"url": page.url, "title": await page.title()}
        if step.action is ActionKind.CLICK:
            await page.click(step.selector or "", timeout=10_000)
            return {"clicked": step.selector}
        if step.action is ActionKind.TYPE:
            await page.fill(step.selector or "", step.text or "", timeout=10_000)
            return {"filled": step.selector}
        if step.action is ActionKind.EXTRACT:
            return await self._extract(step)
        if step.action is ActionKind.WAIT:
            await page.wait_for_timeout(step.wait_ms or 1_000)
            return {"waited_ms": step.wait_ms or 1_000}
        if step.action is ActionKind.SCREENSHOT:
            out = Path("screenshots")
            out.mkdir(exist_ok=True)
            path = out / f"step-{uuid4().hex[:8]}.png"
            await page.screenshot(path=path, full_page=True)
            return {"screenshot": str(path)}
        raise ValueError(f"BrowserTool cannot run action: {step.action}")

    async def _extract(self, step: FlowStep) -> dict:
        if step.selector:
            # Field-aware extraction: selector matches each row, fields map column
            # names to CSS selectors within a row (links resolve to their href).
            rows = await self._page.evaluate(
                """({rowsSel, fields}) => Array.from(document.querySelectorAll(rowsSel)).map(row => {
                     const rec = {};
                     for (const [name, sel] of Object.entries(fields || {})) {
                       const el = row.querySelector(sel);
                       if (!el) { rec[name] = null; continue; }
                       rec[name] = el.tagName === 'A' && el.getAttribute('href')
                         ? el.href  // absolute form
                         : el.innerText.trim();
                     }
                     return rec;
                   })""",
                {"rowsSel": step.selector, "fields": step.fields or {}},
            )
            return {"rows": rows}
        # Fallback: scrape every HTML table on the page.
        rows = await self._page.evaluate(
            """() => Array.from(document.querySelectorAll('table tr')).map(tr =>
                 Array.from(tr.querySelectorAll('th,td')).map(td => td.innerText.trim()))"""
        )
        return {"rows": rows}

    async def stop(self) -> None:
        if self.started:
            await self._browser.close()
            await self._pw.stop()
            self.started = False
