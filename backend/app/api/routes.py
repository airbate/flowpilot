from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.executor import FlowExecutor
from app.agent.planner import make_plan, revise_plan
from app.agent.schemas import FlowPlan

router = APIRouter(prefix="/api")


class PlanRequest(BaseModel):
    goal: str


class ReviseRequest(BaseModel):
    plan: FlowPlan
    instruction: str


@router.post("/plan", response_model=FlowPlan)
async def plan_flow(body: PlanRequest) -> FlowPlan:
    try:
        return await make_plan(body.goal)
    except RuntimeError as exc:  # missing NEBIUS_API_KEY etc.
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/plan/revise", response_model=FlowPlan)
async def revise_flow(body: ReviseRequest) -> FlowPlan:
    try:
        return await revise_plan(body.plan, body.instruction)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/run")
async def run_flow(plan: FlowPlan) -> StreamingResponse:
    async def sse():
        executor = FlowExecutor(plan)
        async for event in executor.run():
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(sse(), media_type="text/event-stream")
