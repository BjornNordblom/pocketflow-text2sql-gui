from typing import Any, Dict

import httpx

from .settings import OPENROUTER_API_KEY, OPENROUTER_MODEL


def call_llm(prompt: str) -> str:
    """
    Calls OpenRouter /v1/completions with a simple prompt and returns the first completion text.

    This is a synchronous helper suitable for FastAPI sync contexts.
    If you prefer async, convert to httpx.AsyncClient and make this an async def.
    """
    if not OPENROUTER_API_KEY:
        # Keep behavior aligned with app.py, which maps NotImplementedError to 501.
        raise NotImplementedError(
            "OPENROUTER_API_KEY is not set. Export it in the environment to enable LLM calls."
        )

    url = "https://openrouter.ai/api/v1/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
        "model": OPENROUTER_MODEL,
        "prompt": prompt,
    }

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as e:
        # This will surface as 500 via FastAPI error handling.
        raise RuntimeError(f"OpenRouter request failed: {e}") from e

    if resp.status_code < 200 or resp.status_code >= 300:
        # Include response body for easier debugging.
        raise RuntimeError(f"OpenRouter error {resp.status_code}: {resp.text}")

    try:
        data = resp.json()
    except ValueError as e:
        raise RuntimeError("OpenRouter response was not valid JSON") from e

    # Expected schema: { choices: [ { text: "..." , ... } ], ... }
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError(f"OpenRouter response missing choices: {data}")

    text = choices[0].get("text")
    if not isinstance(text, str):
        raise RuntimeError(f"OpenRouter choice missing text: {choices[0]}")

    return text.strip()
