from app.agent.planner import mock_plan, parse_plan
from app.agent.schemas import ActionKind, FlowPlan


def test_mock_plan_is_runnable_without_keys():
    plan = mock_plan("grab something")
    assert plan.steps[0].action is ActionKind.NAVIGATE
    assert all(s.url or s.wait_ms or s.selector or s.action is ActionKind.SCREENSHOT for s in plan.steps)


def test_parse_plan_tolerates_fences_and_prose():
    raw = """Here is the plan:
```json
{"goal": "Collect pricing", "summary": "s",
 "steps": [{"action": "tavily_search", "description": "find", "query": "pricing"}]}
```
Done!"""
    plan = parse_plan(raw, fallback_goal="Collect pricing")
    assert plan.steps[0].action is ActionKind.TAVILY_SEARCH


def test_parse_plan_drops_invalid_steps_but_keeps_valid_ones():
    raw = """{"goal": "g", "steps": [
        {"action": "navigate", "description": "ok", "url": "https://x.com"},
        {"action": "teleport", "description": "not a real action"},
        {"description": "missing action"}
    ]}"""
    plan = parse_plan(raw, fallback_goal="g")
    assert [s.action for s in plan.steps] == [ActionKind.NAVIGATE]


def test_plan_dsl_extensions_validate():
    plan = FlowPlan.model_validate(
        {
            "goal": "g",
            "steps": [
                {"action": "tavily_search", "description": "s", "query": "q"},
                {"action": "tavily_extract", "description": "e", "from_step": 0},
                {"action": "extract", "description": "x", "selector": "tr", "fields": {"title": "a"}},
            ],
        }
    )
    assert plan.steps[1].from_step == 0
    assert plan.steps[2].fields == {"title": "a"}
