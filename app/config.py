from __future__ import annotations

import os
from dataclasses import dataclass

try:
    # Load variables from a local .env file if present
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # python-dotenv may not be installed; ignore if missing
    pass


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openweather_api_key: str | None
    default_city: str
    debug: bool
    llm_provider: str
    google_api_key: str | None


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openweather_api_key=os.getenv("OPENWEATHER_API_KEY"),
        default_city=os.getenv("DEFAULT_CITY", "San Francisco"),
        debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"},
        llm_provider=os.getenv("LLM_PROVIDER", "gemini").lower(),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
