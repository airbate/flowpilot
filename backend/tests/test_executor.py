import pytest

from app.agent.executor import FlowExecutor
from app.agent.schemas import ActionKind, EventKind, FlowPlan, FlowStep


def _plan(*actions: ActionKind) -> FlowPlan:
    return FlowPlan(goal="g", steps=[FlowStep(action=a, description=str(a)) for a in actions])


async def test_event_lifecycle_and_rows(monkeypatch):
    ex = FlowExecutor(_plan(ActionKind.EXTRACT, ActionKind.SCREENSHOT))

    async def fake_run_step(index, step):
        if step.action is ActionKind.EXTRACT:
            return {"rows": [{"title": "x", "price": "1"}, ["a", "b"]]}
        return {"screenshot": "s.png"}

    monkeypatch.setattr(ex, "_run_step", fake_run_step)
    events = [e async for e in ex.run()]

    kinds = [e.kind for e in events]
    assert kinds[0] is EventKind.PLAN_CREATED
    assert kinds[-1] is EventKind.RUN_FINISHED
    assert kinds.count(EventKind.STEP_FINISHED) == 2
    assert events[-1].data["ok"] is True


def test_collect_rows_wraps_list_rows_keeps_dict_rows():
    ex = FlowExecutor(_plan())
    ex._collect_rows([{"title": "x", "price": "1"}, ["a", "b"], "junk"])
    assert ex.rows == [{"title": "x", "price": "1"}, {"cells": ["a", "b"]}]


async def test_retry_then_fail_emits_retry_and_failure_events(monkeypatch):
    ex = FlowExecutor(_plan(ActionKind.EXTRACT))
    ex.retries = 1
    calls = {"n": 0}

    async def always_fails(index, step):
        calls["n"] += 1
        raise RuntimeError("boom")

    monkeypatch.setattr(ex, "_run_step", always_fails)
    events = [e async for e in ex.run()]

    assert calls["n"] == 2  # first attempt + one retry
    retry_notes = [e for e in events if "retrying" in e.message]
    assert len(retry_notes) == 1
    failed = [e for e in events if e.kind is EventKind.STEP_FAILED]
    assert len(failed) == 1 and "after 2 attempt(s)" in failed[0].message
    assert events[-1].data["ok"] is False


async def test_retry_succeeds_on_second_attempt(monkeypatch):
    ex = FlowExecutor(_plan(ActionKind.EXTRACT))
    ex.retries = 1
    calls = {"n": 0}

    async def flaky(index, step):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("transient")
        return {"rows": [{"title": "x"}]}

    monkeypatch.setattr(ex, "_run_step", flaky)
    events = [e async for e in ex.run()]

    assert calls["n"] == 2
    assert any(e.kind is EventKind.STEP_FINISHED for e in events)
    assert events[-1].data["ok"] is True


async def test_fail_fast_on_step_error(monkeypatch):
    ex = FlowExecutor(_plan(ActionKind.EXTRACT, ActionKind.WAIT))

    async def boom(index, step):
        raise RuntimeError("no keys")

    monkeypatch.setattr(ex, "_run_step", boom)
    events = [e async for e in ex.run()]

    kinds = [e.kind for e in events]
    assert EventKind.STEP_FAILED in kinds
    assert kinds[-1] is EventKind.RUN_FINISHED
    assert events[-1].data["ok"] is False
    assert "no keys" in ex.errors[0]


def test_collect_urls_from_search_output():
    ex = FlowExecutor(_plan())
    ex._step_outputs[0] = {"top_results": [{"url": "https://a.com"}, {"url": None}, {"url": "https://b.com"}]}
    assert ex._urls_from_step(0) == ["https://a.com", "https://b.com"]
    assert ex._urls_from_step(None) == []
