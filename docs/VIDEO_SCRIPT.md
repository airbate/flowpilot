# Demo Video Script (≤3:00, English narration, YouTube public)

> Rules: ≤3 minutes, public YouTube, English voiceover explaining tech usage.
> Recording checklist: 1080p+, clean browser profile, rehearse both scenarios once, captions on.

## Shot list

| Time | Screen | Narration |
|---|---|---|
| 0:00–0:20 | Slide: messy spreadsheet → exhausted person | "Every week, operations people open the same twenty websites and copy the same fields into the same spreadsheet. RPA tools make you build flowcharts. AI agents demo well — and then click the wrong button. This is FlowPilot." |
| 0:20–0:55 | FlowPilot UI: type goal, press Plan, show plan preview | "You describe the job in one sentence. FlowPilot's planner — NVIDIA Nemotron running on Nebius Token Factory — turns it into a step plan. And because it's a plan, not generated code, you can read it, approve it, or revise it in plain English before anything happens." |
| 0:55–1:40 | Press Run; live step timeline; open the results table; export CSV | "Watch the execution live. For static pages, FlowPilot never opens a browser — Tavily's Search and Extract APIs bring the content straight in, and results from a search feed directly into extraction. The browser only wakes up for steps that truly need clicking. Collected content is normalized into a table by Nemotron, and exports to CSV in one click." |
| 1:40–2:10 | Scenario 2: an interactive flow (search box → results table) | "When interaction is unavoidable, Playwright drives a headless browser — but the model plans the steps as a restricted set of actions, and the executor runs them deterministically. Every step captures screenshot evidence, so every run is replayable and auditable." |
| 2:10–2:40 | Architecture slide | "Everything runs on Nebius Token Factory: Nemotron plans the work, revises plans on request, and normalizes the data. Tavily is the agent's web-access layer — search, extract, and crawl as first-class plan steps, not an afterthought. Failures retry automatically, and the human stays in the loop." |
| 2:40–3:00 | Slide: repo + demo links, closing line | "FlowPilot: plain-English web automation that's reliable because it's planned, approved, and replayable. Links below — thanks for watching." |

## Recording notes

- Total narration ≈ 430 words ≈ 2:50 at natural pace. Leave 2–3 s padding per cut.
- Scenario 1 (Tavily-first): "collect support/pricing info for these 5 companies" — plan shows tavily_search → tavily_extract (from_step) → normalize.
- Scenario 2 (browser): a site search flow ending in a field-aware table extract + CSV export.
- Show the revision round-trip (type "only grab prices" → plan updates) — it is the strongest human-in-the-loop beat.
- If a step fails on camera, let the retry event show, then continue — resilience is part of the story.
