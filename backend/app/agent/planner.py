"""NL goal -> FlowPlan via Nemotron on Nebius Token Factory."""

import json

from pydantic import ValidationError

from app.agent.schemas import ActionKind, FlowPlan, FlowStep
from app.config import get_settings
from app.llm.nebius_client import complete

SYSTEM_PROMPT = """You are FlowPilot's planner. Convert the user's web task into a replayable step plan.

Available actions (the JSON "action" field, with their parameters):
- tavily_search  {query}                      — live web search; use it to locate the right sites
- tavily_extract {urls | from_step}           — pull clean content from URLs; PREFER this over the browser
                                                 for static pages. from_step: reuse the URLs found by an
                                                 earlier tavily_search step (0-based step index).
- normalize      {}                           — turn all content collected so far into a clean table
                                                 ({"columns": [...], "rows": [{...}]}); always end plans
                                                 whose goal is a table/report with this step.
- navigate       {url}                        — open a page in the browser
- click          {selector}                   — click an element
- type           {selector, text}             — fill an input
- extract        {selector?, fields?}         — scrape rows from the current page; selector matches each
                                                 row, fields maps column names to CSS selectors within
                                                 a row, e.g. {"title": "h3 a", "price": ".price"}.
                                                 Without selector, scrapes HTML tables.
- wait           {wait_ms}                    — pause for dynamic content
- screenshot     {}                           — capture the current page as replay evidence

Rules:
1. Prefer tavily_search + tavily_extract; only use browser steps when real interaction is unavoidable.
2. Keep steps small and strictly ordered; never merge two actions into one step.
3. Selectors must be concrete CSS selectors; when unsure, add a screenshot step before interacting.
4. If the user's goal mentions specific websites, navigate/extract directly instead of searching first.
5. Output STRICT JSON only, matching:
{"goal": "...", "summary": "one-line plan summary",
 "steps": [{"action": "...", "description": "why this step", ...params}]}"""


async def make_plan(goal: str) -> FlowPlan:
    if get_settings().mock_planner:
        return mock_plan(goal)
    raw = await complete(SYSTEM_PROMPT, goal, json_mode=True)
    return parse_plan(raw, fallback_goal=goal)


def mock_plan(goal: str) -> FlowPlan:
    """Deterministic plan for demos and CI when no Nebius key is configured."""
    return FlowPlan(
        goal=goal,
        summary="[mock planner] minimal browser demo",
        steps=[
            FlowStep(action=ActionKind.NAVIGATE, description="Open example.com", url="https://example.com"),
            FlowStep(action=ActionKind.WAIT, description="Let the page settle", wait_ms=500),
            FlowStep(
                action=ActionKind.EXTRACT,
                description="Scrape the page heading and link as a sanity check",
                selector="div",
                fields={"heading": "h1", "link": "a"},
            ),
            FlowStep(action=ActionKind.SCREENSHOT, description="Capture replay evidence"),
        ],
    )


def parse_plan(raw: str, fallback_goal: str) -> FlowPlan:
    """Tolerant JSON extraction — models occasionally wrap JSON in prose or fences."""
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end <= start:
        raise ValueError(f"Planner returned non-JSON output: {raw[:200]!r}")
    data = json.loads(raw[start : end + 1])
    data.setdefault("goal", fallback_goal)
    try:
        return FlowPlan.model_validate(data)
    except ValidationError:
        # Models sometimes emit action params at the wrong nesting level; keep the
        # steps that validate and drop the rest rather than failing the whole plan.
        steps = [s for s in data.get("steps", []) if _valid_step(s)]
        data["steps"] = steps
        return FlowPlan.model_validate(data)


def _valid_step(s: dict) -> bool:
    try:
        FlowStep.model_validate(s)
        return True
    except ValidationError:
        return False
