"""Async Tavily Search/Extract client (https://tavily.com)."""

import httpx

from app.config import get_settings


class TavilyTool:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.tavily_api_key:
            raise RuntimeError("TAVILY_API_KEY is not set — copy .env.example to .env and fill it in")
        self._client = httpx.AsyncClient(
            base_url=settings.tavily_base_url,
            headers={"Authorization": f"Bearer {settings.tavily_api_key}"},
            timeout=30,
        )

    async def search(self, query: str, *, max_results: int = 5, depth: str = "basic") -> dict:
        resp = await self._client.post(
            "/search",
            json={"query": query, "max_results": max_results, "search_depth": depth},
        )
        resp.raise_for_status()
        return resp.json()

    async def extract(self, urls: list[str]) -> dict:
        resp = await self._client.post("/extract", json={"urls": urls})
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        await self._client.aclose()
