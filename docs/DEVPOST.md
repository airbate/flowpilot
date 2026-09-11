# Devpost Project Description (submission-ready draft)

> Paste into the Devpost "Project Description" form. English, per the rules.

## Inspiration

Operations people, sellers, and researchers lose hours every day to the same loop: open ten competitor sites, copy the same fields into a spreadsheet, re-check them next week. Traditional RPA tools demand flowcharts and selectors up front; generic AI agents demo well but are too unreliable to touch a real browser.

## What it does

FlowPilot turns a plain-English sentence into a **reliable, replayable browser workflow**:

1. **Plan** — you type the goal ("collect support emails from these 20 companies' pricing pages"). NVIDIA Nemotron, served by Nebius Token Factory, emits a step plan as a restricted JSON DSL.
2. **Approve** — the plan is previewed in the UI. You can revise it in plain English ("step 2: only grab prices") before anything runs. Humans stay in the loop.
3. **Execute** — a deterministic executor runs the plan. Static content comes from **Tavily** Search/Extract/Crawl; the headless browser (Playwright) only opens when real interaction is unavoidable. Every step streams live events to the UI; every browser step can capture screenshot evidence.
4. **Collect** — collected raw content is normalized into a clean table by Nemotron, rendered in the app, and exportable as CSV.

## How we built it

- **Backend**: Python + FastAPI; SSE for live execution events.
- **Planner**: NVIDIA Nemotron (Nemotron-3-Super, auto-resolved against the account's model list) via Nebius Token Factory's OpenAI-compatible API, JSON mode. The LLM never generates code — it plans over a fixed action enum, and a deterministic executor runs it. That single decision makes runs reviewable, replayable, and safe.
- **Web access**: Tavily `/search`, `/extract`, `/crawl`, `/map`. Tavily is the agent's eyes, not a bolt-on search box: the planner prefers Tavily for anything static (`from_step` chaining feeds URLs from a search straight into extraction), and the browser handles only what truly needs clicking.
- **Browser**: Playwright (headless Chromium) with field-aware extraction — the plan declares *which* columns to scrape and *where* they live, so the model reasons about structure while the executor stays deterministic.
- **Frontend**: React + Vite — plan preview, revision, live step timeline, results table, CSV export.
- **Verified end-to-end**: the browser pipeline was tested live against real sites; a keyless mock-planner mode keeps demos and CI self-contained.

## Challenges we ran into

- Making LLM browser automation *dependable*: we solved it with the restricted DSL + human approval + per-step retries + screenshot evidence, instead of trusting generated scripts.
- Keeping a solo, 7-week scope honest: we cut multi-user accounts, anti-bot evasion, and mobile from day one.

## Accomplishments we're proud of

- A complete product loop (plan → approve → execute → replay → export), not a PoC.
- Tavily used the way it was built to be used: as the web-access layer of an agent, with the browser as fallback.
- A UI a non-engineer can operate without explanation.

## What we learned

- Structured output (JSON mode) from Nemotron is dependable enough to be the *contract* of a system, not just a chat reply — planning quality is a prompting + schema-design problem.
- The cheapest reliable automation is the one that never opens a browser.

## What's next

- Scheduled monitoring flows (watch a pricing page daily, diff the table).
- Human takeover mid-run: when a step fails, hand the browser to the person and resume.
- Plan marketplace: share replayable workflow templates.

## Built with

nebius-token-factory · nvidia-nemotron · tavily-api · python · fastapi · playwright · react · vite · docker

## Links

- GitHub: https://github.com/airbate/flowpilot
- Demo: (deployed URL — see docs/DEPLOYMENT.md)
- Video: (YouTube link — script in docs/VIDEO_SCRIPT.md)

## Tracks & prizes

- Track: **Best Apps and Agents**
- Bonus: **Best Use of Tavily**
