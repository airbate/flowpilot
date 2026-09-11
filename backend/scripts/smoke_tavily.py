"""W1 gate: verify Tavily Search/Extract connectivity.

Run from backend/ with TAVILY_API_KEY in .env:
    cp .env.example .env   # fill in TAVILY_API_KEY
    python -m scripts.smoke_tavily
"""

import asyncio

from app.tools.tavily import TavilyTool


async def main() -> None:
    tavily = TavilyTool()
    try:
        result = await tavily.search("Nebius Token Factory Nemotron", max_results=3)
        for r in result.get("results", []):
            print(f"- {r.get('title')}  {r.get('url')}")
        print(f"Tavily OK, {len(result.get('results', []))} results")
    finally:
        await tavily.close()


if __name__ == "__main__":
    asyncio.run(main())
