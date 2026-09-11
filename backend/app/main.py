from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import get_settings

app = FastAPI(title="FlowPilot", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

# Replay evidence captured during runs (BrowserTool writes here relative to CWD).
_shots = Path("screenshots")
_shots.mkdir(exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=_shots), name="screenshots")


@app.get("/health")
async def health() -> dict:
    s = get_settings()
    return {
        "status": "ok",
        "service": "flowpilot",
        "nemotron": bool(s.nebius_api_key),
        "tavily": bool(s.tavily_api_key),
        "mock_planner": s.mock_planner,
        "step_retries": s.step_retries,
    }
