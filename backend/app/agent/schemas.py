"""Core data models: the constrained step DSL the planner emits and the executor runs.

Design decision (see docs/立项文档.md): the LLM never writes code — it emits a
JSON plan over a fixed action enum, and a deterministic executor runs it. That
keeps runs replayable, reviewable, and safe.
"""

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class ActionKind(str, Enum):
    TAVILY_SEARCH = "tavily_search"
    TAVILY_EXTRACT = "tavily_extract"
    TAVILY_CRAWL = "tavily_crawl"
    TAVILY_MAP = "tavily_map"
    NORMALIZE = "normalize"  # LLM turns collected content into table rows
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    EXTRACT = "extract"  # scrape structured rows from the current page
    WAIT = "wait"
    SCREENSHOT = "screenshot"


class FlowStep(BaseModel):
    action: ActionKind
    description: str = Field(..., description="Human-readable: what this step does and why")
    url: str | None = None            # navigate
    selector: str | None = None       # click / type / extract (row selector)
    text: str | None = None           # type
    query: str | None = None          # tavily_search
    urls: list[str] | None = None     # tavily_extract
    from_step: int | None = Field(    # tavily_extract: reuse the URLs an earlier step found
        None, description="0-based index of an earlier tavily_search step"
    )
    fields: dict[str, str] | None = Field(  # extract: column name -> CSS selector within each row
        None, description='e.g. {"title": "h3 a", "price": ".price"}'
    )
    wait_ms: int | None = None        # wait


class FlowPlan(BaseModel):
    goal: str
    summary: str = ""
    steps: list[FlowStep] = Field(default_factory=list)


class EventKind(str, Enum):
    PLAN_CREATED = "plan_created"
    STEP_STARTED = "step_started"
    STEP_FINISHED = "step_finished"
    STEP_FAILED = "step_failed"
    RUN_FINISHED = "run_finished"


class ExecutionEvent(BaseModel):
    kind: EventKind
    step_index: int | None = None
    message: str = ""
    data: dict | None = None
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FlowRunResult(BaseModel):
    goal: str
    ok: bool
    rows: list[dict] = Field(default_factory=list, description="Extracted structured results")
    errors: list[str] = Field(default_factory=list)
