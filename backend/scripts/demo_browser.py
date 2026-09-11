"""End-to-end demo that needs NO API keys: runs a canned browser plan through
the real executor + Playwright (Chromium).

Setup (once):  .venv/bin/playwright install chromium
Run:           cd backend && .venv/bin/python -m scripts.demo_browser
"""

import asyncio

from app.agent.executor import FlowExecutor
from app.agent.schemas import ActionKind, EventKind, FlowPlan, FlowStep

PLAN = FlowPlan(
    goal="Sanity check: open example.com and pull its heading and link",
    summary="browser-only demo plan",
    steps=[
        FlowStep(action=ActionKind.NAVIGATE, description="Open example.com", url="https://example.com"),
        FlowStep(action=ActionKind.WAIT, description="Let the page settle", wait_ms=500),
        FlowStep(
            action=ActionKind.EXTRACT,
            description="Scrape heading + link",
            selector="div",
            fields={"heading": "h1", "link": "a"},
        ),
        FlowStep(action=ActionKind.SCREENSHOT, description="Capture replay evidence"),
    ],
)


async def main() -> None:
    ex = FlowExecutor(PLAN)
    async for event in ex.run():
        line = f"[{event.kind.value}] {event.message}"
        if event.kind is EventKind.STEP_FINISHED:
            line += f"  data={event.data}"
        print(line)
    print(f"\nrows collected: {ex.rows}")


if __name__ == "__main__":
    asyncio.run(main())
