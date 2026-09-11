"""W1 gate: verify Nebius Token Factory connectivity and lock in a working Nemotron model.

What it does:
1. Lists the models actually available to your account (GET /models).
2. If PLANNER_MODEL is missing/stale on the platform, auto-picks the best Nemotron
   (Super > Ultra > Nano by preference) and saves it back into backend/.env.
3. Runs a tiny chat completion as a live proof.

Run from backend/ with NEBIUS_API_KEY set in .env:
    python -m scripts.smoke_nebius
"""

import asyncio
from pathlib import Path

from app.config import get_settings
from app.llm.nebius_client import complete, get_client


def pick_model(models: list[str], current: str) -> str | None:
    """Prefer the configured model; otherwise the strongest available Nemotron."""
    if current in models:
        return current

    def rank(m: str) -> tuple[int, int]:
        low = m.lower()
        if "nemotron" not in low:
            return (0, -len(m))
        tier = 3 if "super" in low else 2 if "ultra" in low else 1
        return (tier, -len(m))

    best = max(models, key=rank)
    return best if "nemotron" in best.lower() else None


def save_model_to_env(model: str) -> None:
    env_path = Path(".env")
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    lines = [l for l in lines if not l.startswith("PLANNER_MODEL=")]
    lines.append(f"PLANNER_MODEL={model}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


async def main() -> None:
    settings = get_settings()
    client = get_client()
    page = await client.models.list()
    models = sorted(m.id for m in page.data)
    print(f"endpoint: {settings.nebius_base_url}  ({len(models)} models visible)")

    chosen = pick_model(models, settings.planner_model)
    if chosen is None:
        raise SystemExit(f"No Nemotron model available to this account: {models}")
    if chosen != settings.planner_model:
        save_model_to_env(chosen)
        get_settings.cache_clear()
        print(f"PLANNER_MODEL {settings.planner_model!r} not on platform — switched to {chosen!r} (saved to .env)")
    else:
        print(f"model: {chosen}")

    reply = await complete("Reply with exactly one word: PONG", "ping")
    print(f"Nebius OK, {chosen} replied: {reply!r}")


if __name__ == "__main__":
    asyncio.run(main())
