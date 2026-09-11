"""Thin wrapper over the OpenAI SDK pointed at Nebius Token Factory.

Token Factory serves NVIDIA open models (Nemotron family) behind an
OpenAI-compatible chat completions API, so the stock `openai` client works
once base_url + api_key are set.
"""

from openai import AsyncOpenAI

from app.config import get_settings


def get_client() -> AsyncOpenAI:
    settings = get_settings()
    if not settings.nebius_api_key:
        raise RuntimeError("NEBIUS_API_KEY is not set — copy .env.example to .env and fill it in")
    return AsyncOpenAI(base_url=settings.nebius_base_url, api_key=settings.nebius_api_key)


async def complete(
    system: str,
    user: str,
    *,
    json_mode: bool = False,
    temperature: float = 0.2,
) -> str:
    settings = get_settings()
    client = get_client()
    kwargs: dict = {
        "model": settings.planner_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = await client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""
