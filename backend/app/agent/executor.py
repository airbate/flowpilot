"""Runs a FlowPlan step by step, yielding events (SSE-friendly)."""

import json
from collections.abc import AsyncIterator

from app.agent.schemas import ActionKind, ExecutionEvent, EventKind, FlowPlan, FlowStep
from app.llm.nebius_client import complete
from app.tools.browser import BrowserTool
from app.tools.tavily import TavilyTool

NORMALIZE_PROMPT = """You are FlowPilot's data normalizer. Below is a user's goal and the raw
content collected from the web. Turn it into a clean table.

Return STRICT JSON only: {{"columns": ["..."], "rows": [{{"...": "..."}}]}}
Rules: rows must all have the same keys as columns; keep values short and literal;
drop rows with no usable data; do not invent data that is not in the content.

User goal: {goal}

Collected content:
{content}"""


class FlowExecutor:
    def __init__(self, plan: FlowPlan) -> None:
        self.plan = plan
        self.rows: list[dict] = []
        self.columns: list[str] = []
        self.errors: list[str] = []
        self._content: list[dict] = []  # everything collected for the normalize step
        self._step_outputs: dict[int, dict] = {}
        self._tavily: TavilyTool | None = None
        self._browser: BrowserTool | None = None

    async def run(self) -> AsyncIterator[ExecutionEvent]:
        yield ExecutionEvent(
            kind=EventKind.PLAN_CREATED,
            message=self.plan.summary or self.plan.goal,
            data={"step_count": len(self.plan.steps)},
        )
        try:
            for i, step in enumerate(self.plan.steps):
                yield ExecutionEvent(kind=EventKind.STEP_STARTED, step_index=i, message=step.description)
                try:
                    data = await self._run_step(i, step)
                except Exception as exc:  # fail fast for now; W4 adds retry + human takeover
                    msg = f"step {i} ({step.action.value}) failed: {exc}"
                    self.errors.append(msg)
                    yield ExecutionEvent(kind=EventKind.STEP_FAILED, step_index=i, message=msg)
                    break
                self._step_outputs[i] = data
                yield ExecutionEvent(kind=EventKind.STEP_FINISHED, step_index=i, message=step.description, data=data)
            ok = not self.errors
            yield ExecutionEvent(
                kind=EventKind.RUN_FINISHED,
                message="done" if ok else "finished with errors",
                data={"ok": ok, "row_count": len(self.rows), "errors": self.errors},
            )
        finally:
            if self._browser is not None:
                await self._browser.stop()
            if self._tavily is not None:
                await self._tavily.close()

    async def _run_step(self, index: int, step: FlowStep) -> dict:
        match step.action:
            case ActionKind.TAVILY_SEARCH:
                self._tavily = self._tavily or TavilyTool()
                result = await self._tavily.search(step.query or self.plan.goal)
                results = result.get("results", [])[:5]
                for r in results:
                    self._content.append({"url": r.get("url"), "content": r.get("content", "")})
                return {"top_results": [{"title": r.get("title"), "url": r.get("url")} for r in results]}
            case ActionKind.TAVILY_EXTRACT:
                self._tavily = self._tavily or TavilyTool()
                urls = step.urls or self._urls_from_step(step.from_step)
                if not urls:
                    raise ValueError("tavily_extract needs urls or a from_step pointing at a search")
                result = await self._tavily.extract(urls)
                extracted = result.get("results", [])
                failed = [f.get("url") for f in result.get("failed_results", [])]
                for r in extracted:
                    self._content.append({"url": r.get("url"), "content": r.get("raw_content", "")})
                return {"extracted": [{"url": r.get("url"), "length": len(r.get("raw_content") or "")} for r in extracted],
                        "failed": failed}
            case ActionKind.NORMALIZE:
                return await self._normalize()
            case _:
                self._browser = self._browser or BrowserTool()
                data = await self._browser.run_step(step)
                if step.action is ActionKind.EXTRACT and isinstance(data.get("rows"), list):
                    self._collect_rows(data["rows"])
                return data

    def _urls_from_step(self, from_step: int | None) -> list[str]:
        if from_step is None:
            return []
        urls = []
        for r in self._step_outputs.get(from_step, {}).get("top_results", []):
            if r.get("url"):
                urls.append(r["url"])
        return urls

    async def _normalize(self) -> dict:
        if not self._content:
            raise ValueError("normalize needs prior tavily/extract content — nothing collected yet")
        content_blob = "\n---\n".join(
            f"[{c.get('url', 'browser page')}]\n{(c.get('content') or '')[:2500]}" for c in self._content[:12]
        )
        raw = await complete(
            NORMALIZE_PROMPT.format(goal=self.plan.goal, content=content_blob), "Produce the table now.", json_mode=True
        )
        parsed = json.loads(raw[raw.find("{") : raw.rfind("}") + 1])
        self.columns = parsed.get("columns", [])
        self.rows = [r for r in parsed.get("rows", []) if isinstance(r, dict)]
        return {"columns": self.columns, "rows": self.rows}

    def _collect_rows(self, rows: list) -> None:
        for r in rows:
            if isinstance(r, dict):
                self.rows.append(r)
            elif isinstance(r, list):
                self.rows.append({"cells": r})
