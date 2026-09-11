"""W1 gate: verify Nebius Token Factory connectivity + Nemotron inference.

Run from backend/ with both API keys in .env:
    cp .env.example .env   # fill in NEBIUS_API_KEY
    python -m scripts.smoke_nebius
"""

import asyncio

from app.config import get_settings
from app.llm.nebius_client import complete


async def main() -> None:
    settings = get_settings()
    print(f"endpoint: {settings.nebius_base_url}")
    print(f"model:    {settings.planner_model}")
    reply = await complete("Reply with exactly one word: PONG", "ping")
    print(f"Nebius OK, model replied: {reply!r}")


if __name__ == "__main__":
    asyncio.run(main())
