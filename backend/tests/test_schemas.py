from app.agent.planner import parse_plan
from app.agent.schemas import ActionKind, FlowPlan

SAMPLE = """Here is the plan you asked for:
```json
{"goal": "Collect pricing pages", "summary": "Search then extract",
 "steps": [{"action": "tavily_search", "description": "Find pricing pages", "query": " competitors pricing page"}]}
```
Hope this helps!"""


def test_parse_plan_tolerates_fences_and_prose():
    plan = parse_plan(SAMPLE, fallback_goal="Collect pricing pages")
    assert plan.goal == "Collect pricing pages"
    assert plan.steps[0].action is ActionKind.TAVILY_SEARCH
    assert plan.steps[0].query is not None


def test_plan_validates_minimal_shape():
    plan = FlowPlan.model_validate({"goal": "x", "steps": []})
    assert plan.summary == ""
    assert plan.steps == []
