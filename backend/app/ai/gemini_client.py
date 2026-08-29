from __future__ import annotations
"""
Gemini Client — singleton initialised once at import time.
Works with google-genai >= 1.0.0 SDK.
"""
import logging
import os
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# ── SDK import with graceful degradation ─────────────────────────────────────
try:
    from google import genai
    from google.genai import types as genai_types
    _SDK_OK = True
except ImportError:
    genai = None          # type: ignore
    genai_types = None    # type: ignore
    _SDK_OK = False
    logger.warning("google-genai SDK not installed — Gemini features disabled")


def _get_api_key() -> str:
    """Read from env; support both common naming conventions."""
    return (
        os.environ.get("GEMINI_API_KEY", "")
        or os.environ.get("GOOGLE_API_KEY", "")
    )


def _get_model() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


@lru_cache(maxsize=1)
def get_client():
    """Return a configured genai.Client or None if unavailable.
    NOT cached — env vars may be loaded after module import.
    """
    if not _SDK_OK:
        return None
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as exc:
        logger.error("Gemini client init failed: %s", exc)
        return None


def get_model_name() -> str:
    return _get_model()


def is_available() -> bool:
    return get_client() is not None


async def generate_text(
    prompt: str,
    system: str = "",
    temperature: float = 0.3,
    max_output_tokens: int = 1024,
) -> tuple[str, bool]:
    """
    Returns (text, is_ai_generated).
    Never raises — falls back to empty string on any error.
    """
    c = get_client()
    if c is None:
        return "", False

    model = get_model_name()
    contents: list[Any] = []
    if system:
        contents.append(system)
    contents.append(prompt)

    try:
        config = genai_types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        resp = c.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
        text = resp.text or ""
        return text.strip(), True
    except Exception as exc:
        logger.warning("Gemini generate_text failed: %s", exc)
        return "", False


async def generate_json(
    prompt: str,
    system: str = "",
    temperature: float = 0.2,
) -> tuple[dict, bool]:
    """Generate and parse a JSON response."""
    import json as _json
    text, ok = await generate_text(prompt, system=system, temperature=temperature)
    if not ok or not text:
        return {}, False
    # Strip markdown fences if present
    clean = text.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        return _json.loads(clean), True
    except Exception:
        return {"raw": text}, True


# Module-level convenience — call get_client() at request time, not import time
model_name = _get_model()
