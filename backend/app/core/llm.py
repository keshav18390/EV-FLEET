"""
Unified LLM client. Works with any OpenAI-compatible endpoint
(OpenAI, Groq, OpenRouter, Gemini's OpenAI-compat layer) via the `openai` SDK.
Claude (Anthropic) is called through its native Messages API since it isn't
OpenAI-schema compatible.

Design goal: NEVER raise an unhandled exception. Every failure mode returns
a friendly, typed result the API/agents can show to the user.
"""
from dataclasses import dataclass
from typing import Optional

import httpx
from openai import OpenAI, AuthenticationError, APIConnectionError, APIError

from app.core.config import settings


@dataclass
class LLMResult:
    success: bool
    text: str
    error_code: Optional[str] = None  # "no_key" | "invalid_key" | "connection" | "unknown"


def _call_claude_native(prompt: str, system: str) -> LLMResult:
    try:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.CLAUDE_API_KEY or "",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.active_model,
                "max_tokens": 800,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30.0,
        )
        if resp.status_code == 401:
            return LLMResult(False, "Invalid API key.", "invalid_key")
        resp.raise_for_status()
        data = resp.json()
        text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
        return LLMResult(True, text or "No response generated.")
    except httpx.HTTPStatusError as e:
        return LLMResult(False, "Invalid API key or request rejected by provider.", "invalid_key")
    except httpx.RequestError:
        return LLMResult(False, "Could not reach the LLM provider. Please check your connection.", "connection")
    except Exception:
        return LLMResult(False, "Something went wrong contacting the AI provider.", "unknown")


def call_llm(prompt: str, system: str = "You are a helpful fleet operations assistant.") -> LLMResult:
    """Main entry point used by all agents. Handles missing/invalid keys gracefully."""
    if not settings.has_llm_key:
        return LLMResult(False, "API key not configured.", "no_key")

    provider = settings.LLM_PROVIDER.lower()

    if provider == "claude":
        return _call_claude_native(prompt, system)

    # OpenAI-compatible providers: openai, groq, openrouter, gemini
    try:
        client = OpenAI(api_key=settings.active_api_key, base_url=settings.active_base_url)
        completion = client.chat.completions.create(
            model=settings.active_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.4,
        )
        text = completion.choices[0].message.content or "No response generated."
        return LLMResult(True, text)
    except AuthenticationError:
        return LLMResult(False, "Invalid API key.", "invalid_key")
    except APIConnectionError:
        return LLMResult(False, "Could not reach the LLM provider. Please check your connection.", "connection")
    except APIError:
        return LLMResult(False, "The AI provider returned an error. Please try again.", "unknown")
    except Exception:
        return LLMResult(False, "Something went wrong contacting the AI provider.", "unknown")
