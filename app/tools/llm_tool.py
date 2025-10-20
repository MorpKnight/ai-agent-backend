from __future__ import annotations

from typing import AsyncGenerator, Optional

from app.config import get_settings

try:
    from openai import AsyncOpenAI
except Exception:  # pragma: no cover - package may not be installed
    AsyncOpenAI = None  # type: ignore[assignment]

import httpx


async def ask_llm(prompt: str) -> str:
    settings = get_settings()
    provider = settings.llm_provider
    if provider == "gemini":
        if not settings.google_api_key:
            return f"[mocked llm] You asked: '{prompt}'. No GOOGLE_API_KEY configured."
        # REST call to Generative Language API (Gemini 1.5 Flash for responsiveness)
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        params = {"key": settings.google_api_key}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(url, params=params, json=payload)
                r.raise_for_status()
                data = r.json()
            candidates = data.get("candidates") or []
            if not candidates:
                return ""
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
            return text
        except httpx.HTTPStatusError as e:
            return f"LLM request failed: {e.response.status_code} {e.response.text}"
        except Exception as e:  # noqa: BLE001
            return f"LLM request failed: {e}"
    else:
        # Default to OpenAI if configured
        api_key = settings.openai_api_key
        if not api_key or AsyncOpenAI is None:
            # Mock response
            return f"[mocked llm] You asked: '{prompt}'. I cannot access an LLM without an API key."

        client = AsyncOpenAI(api_key=api_key)
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:  # noqa: BLE001
            return f"LLM request failed: {e}"


async def ask_llm_stream(prompt: str) -> AsyncGenerator[str, None]:
    settings = get_settings()
    if settings.llm_provider == "gemini":
        # Gemini streaming via REST is supported by a different endpoint; for simplicity, chunk non-stream result
        text = await ask_llm(prompt)
        for i in range(0, len(text), 32):
            yield text[i : i + 32]
        return
    # OpenAI streaming path
    api_key = settings.openai_api_key
    if not api_key or AsyncOpenAI is None:
        text = await ask_llm(prompt)
        for i in range(0, len(text), 32):
            yield text[i : i + 32]
        return
    client = AsyncOpenAI(api_key=api_key)
    try:
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            stream=True,
        )
        async for event in stream:
            delta = event.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:  # noqa: BLE001
        yield f"[stream error] {e}"


def is_llm_query(query: str) -> bool:
    # Fallback when neither math nor weather clearly match
    return True
