# FlowPilot

[![CI](https://github.com/airbate/flowpilot/actions/workflows/ci.yml/badge.svg)](https://github.com/airbate/flowpilot/actions/workflows/ci.yml)

> Plain-English web process automation copilot.
> **NVIDIA Nemotron** plans the steps (on **Nebius Token Factory**), **Tavily** reads the live web, and **Playwright** executes only the steps that truly need a browser.

Entry for the [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/) — Track: **Best Apps and Agents** + **Best Use of Tavily**. Roadmap and sponsor-motive analysis in [docs/立项文档.md](docs/立项文档.md) (Chinese; English write-up ships with the Devpost submission).

## Status: working end-to-end

The full pipeline runs today: **goal → plan (JSON DSL) → human approval / plain-English revision → step-by-step execution with live SSE events → structured results + CSV export**, with per-step automatic retries and screenshot replay evidence.

- ✅ **Verified live**: browser path (navigate → field-aware extraction → screenshot) against real sites, over HTTP with SSE streaming.
- 🔑 **Plug in keys and it goes fully autonomous**: with `NEBIUS_API_KEY` + `TAVILY_API_KEY` set, the Nemotron planner, plan revision, normalize step, and Tavily search/extract/crawl/map activate (run the smoke scripts below first).
- 🧪 `MOCK_PLANNER=1` serves a deterministic canned plan — demo and CI work with zero API keys.

## How it works

```
Browser UI (React, :5173)
   │  goal in plain English          POST /api/plan
   │  plain-English revision         POST /api/plan/revise
   ▼
FastAPI (:8000) ── Planner ────── Nemotron via Nebius Token Factory (JSON-mode)
   │  replayable step plan (restricted JSON DSL, human-approved)
   ▼
FlowExecutor ──┬─ TavilyTool (/search, /extract, /crawl, /map)  ← static web content
               ├─ normalize step (Nemotron turns collected content into table rows)
               └─ BrowserTool (Playwright, headless) ← interactive steps only
   │  live events (SSE) · per-step retries · screenshot evidence at /screenshots/
   ▼
Step timeline + results table + CSV export
```

Key design choices:

1. **The LLM never generates code.** It emits a plan over a fixed action enum (`tavily_search`, `tavily_extract`, `tavily_crawl`, `tavily_map`, `normalize`, `navigate`, `click`, `type`, `extract`, `wait`, `screenshot`) that a deterministic executor runs — replayable, reviewable, safe.
2. **Tavily first, browser as fallback.** Static content comes from Tavily (with `from_step` chaining: extract consumes the URLs a search step found); the browser only opens when real interaction is unavoidable.
3. **Human in the loop.** Plans are previewed, revisable in plain English, and approved before execution; every browser step captures screenshot evidence for replay.
4. **Resilience by default.** Steps retry automatically (`STEP_RETRIES`, default 1); failure details stream into the timeline.

## Quick start

Backend (Python 3.11+):

```bash
cd backend
cp .env.example .env          # fill in NEBIUS_API_KEY + TAVILY_API_KEY (or leave empty + MOCK_PLANNER=1)
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/playwright install chromium   # once, for browser steps

# no-key sanity checks
MOCK_PLANNER=1 .venv/bin/uvicorn app.main:app --reload   # then open the frontend
.venv/bin/python -m scripts.demo_browser                 # real browser e2e, no keys needed

# with keys configured
.venv/bin/python -m scripts.smoke_nebius   # W1 gate: Nebius connectivity
.venv/bin/python -m scripts.smoke_tavily   # W1 gate: Tavily connectivity
```

Frontend (Node 18+):

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173 (proxies /api to :8000)
```

Tests:

```bash
cd backend && .venv/bin/python -m pytest tests -q
```

Or run the whole stack in Docker:

```bash
docker compose up --build -d     # http://localhost:8080 (mock planner unless keys provided)
```

## Docs

- [docs/立项文档.md](docs/立项文档.md) — charter, sponsor-motive analysis, weekly roadmap (Chinese)
- [docs/DEVPOST.md](docs/DEVPOST.md) — submission-ready project description (English)
- [docs/VIDEO_SCRIPT.md](docs/VIDEO_SCRIPT.md) — 3-minute demo video script
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — local / Docker / public demo URL guide
- [docs/feedback-notes.md](docs/feedback-notes.md) — Nebius/NVIDIA/Tavily tooling feedback log

## License

Apache-2.0 (meets the hackathon's open-source license requirement).
