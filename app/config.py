from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openweather_api_key: str | None
    default_city: str
    debug: bool


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openweather_api_key=os.getenv("OPENWEATHER_API_KEY"),
        default_city=os.getenv("DEFAULT_CITY", "San Francisco"),
        debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"},
    )
