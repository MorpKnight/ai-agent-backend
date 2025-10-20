from __future__ import annotations

from typing import AsyncGenerator, Optional

from app.config import get_settings

try:
    from openai import AsyncOpenAI
except Exception:  # pragma: no cover - package may not be installed
    AsyncOpenAI = None  # type: ignore[assignment]


async def ask_llm(prompt: str) -> str:
    settings = get_settings()
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
    api_key = settings.openai_api_key
    if not api_key or AsyncOpenAI is None:
        # Mock streaming by chunking the static string
        text = await ask_llm(prompt)
        for i in range(0, len(text), 20):
            yield text[i : i + 20]
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
        # Yield a single error chunk
        yield f"[stream error] {e}"


def is_llm_query(query: str) -> bool:
    # Fallback when neither math nor weather clearly match
    return True
