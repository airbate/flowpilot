# Deployment Guide

Three ways to run FlowPilot, from laptop to public demo URL.

## 1 · Local development

```bash
# backend
cd backend
cp .env.example .env            # add keys, or leave empty for mock mode
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/playwright install chromium
MOCK_PLANNER=1 .venv/bin/uvicorn app.main:app --reload   # keyless demo
#   or (real planner):  .venv/bin/uvicorn app.main:app --reload

# frontend
cd ../frontend && npm install && npm run dev   # http://localhost:5173
```

## 2 · Docker Compose (single host)

```bash
NEBIUS_API_KEY=... TAVILY_API_KEY=... MOCK_PLANNER=0 docker compose up --build -d
# no keys yet? just:  docker compose up --build -d   (mock planner on)
# app: http://localhost:8080
```

The stack is: nginx (frontend + reverse proxy) → FastAPI backend → Nebius Token Factory / Tavily. Screenshots persist in the `shots` volume and are served under `/screenshots/`.

## 3 · Public demo URL (submission requirement)

The hackathon requires an accessible Demo URL (Physical AI exempt). Options, cheapest first:

1. **Small VPS** (any provider, 2 vCPU / 4 GB): install Docker, `git clone` + `docker compose up -d`, point a domain, put Caddy or the host's nginx in front for automatic HTTPS.
2. **Nebius AI Cloud VM** (recommended for the narrative): the whole app then runs on Nebius end to end — inference on Token Factory, hosting on AI Cloud. Steps: create VM (Ubuntu) → install Docker → clone repo → compose up → attach floating IP → HTTPS via Caddy.
3. **Tunnel for quick shares**: `cloudflared tunnel` or `ngrok` to expose the compose stack while developing (fine for a demo day, use 1/2 for the submission link).

### Pre-submission checklist for the demo URL

- [ ] `GET /health` returns 200 with `nemotron: true` (not mock mode)
- [ ] Both demo scenarios complete end-to-end through the public URL
- [ ] HTTPS valid; SSE events stream live (no buffering — see nginx.conf)
- [ ] Screenshots render under `/screenshots/`
- [ ] Restart-safe: `docker compose up -d` survives reboot (`restart: unless-stopped` optional)
