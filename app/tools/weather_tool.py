from __future__ import annotations

import os
from typing import Optional

import httpx

from app.config import get_settings


async def fetch_weather(query: str) -> str:
    settings = get_settings()
    city = extract_city_from_query(query) or settings.default_city
    api_key = settings.openweather_api_key

    if not api_key:
        # Mock response when no API key configured
        return f"It's 24°C and sunny in {city}. (mocked)"

    # Use OpenWeatherMap current weather data API
    params = {"q": city, "appid": api_key, "units": "metric"}
    url = "https://api.openweathermap.org/data/2.5/weather"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        return f"Weather lookup failed: {e.response.status_code} {e.response.text}"
    except Exception as e:  # noqa: BLE001
        return f"Weather lookup failed: {e}"

    try:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].capitalize()
        name = data.get("name", city)
        return f"It's {temp}°C and {desc} in {name}."
    except Exception:  # noqa: BLE001
        return f"Could not parse weather data for {city}."


def extract_city_from_query(query: str) -> Optional[str]:
    q = query.strip()
    # Very naive extraction: look for 'in <City>' or 'at <City>' patterns
    lower = q.lower()
    for marker in [" in ", " at "]:
        if marker in lower:
            idx = lower.rfind(marker)
            city_part = q[idx + len(marker) :].strip(" ?.!\t\n\r")
            # Trim extra words like 'today' or 'now'
            for tail in [" today", " now", " right now", " currently"]:
                if city_part.lower().endswith(tail):
                    city_part = city_part[: -len(tail)]
            # Basic title-case normalization
            if city_part:
                return " ".join(w.capitalize() for w in city_part.split())
    return None


def is_weather_query(query: str) -> bool:
    lq = query.lower()
    return any(
        kw in lq
        for kw in [
            "weather",
            "temperature",
            "forecast",
            "rain",
            "snow",
            "wind",
        ]
    )
