from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Nebius Token Factory (OpenAI-compatible inference)
    nebius_api_key: str = ""
    nebius_base_url: str = "https://api.tokenfactory.nebius.com/v1/"
    planner_model: str = "nvidia/llama-3.3-nemotron-super-49b-v1"

    # Tavily
    tavily_api_key: str = ""
    tavily_base_url: str = "https://api.tavily.com"

    # App
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    # Deterministic canned planner for demos/CI when no NEBIUS_API_KEY is available
    mock_planner: bool = False
    # Extra attempts per step after the first one fails (0 = fail fast)
    step_retries: int = 1


@lru_cache
def get_settings() -> Settings:
    return Settings()
