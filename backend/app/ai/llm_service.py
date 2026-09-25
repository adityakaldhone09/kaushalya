from __future__ import annotations
"""
LLM Service — OpenAI integration with deterministic fallback.
The app never crashes when the API key is missing.
"""
import logging
from typing import Any
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are KAUSHALYA, an AI-powered Skill & Employment Intelligence assistant.

STRICT RULES:
1. Use ONLY the data supplied in the user message. Do NOT invent statistics, user information, salary figures, or employment outcomes.
2. Numerical scores and percentages provided by the backend are authoritative — never change them.
3. If required information is missing, explicitly state it is unavailable.
4. Keep responses concise, practical, and action-oriented.
5. Never pretend to know information that was not provided to you.
"""


def _client():
    """Return an OpenAI client or None if unavailable."""
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as exc:
        logger.warning("OpenAI client init failed: %s", exc)
        return None


async def generate(
    prompt: str,
    context: dict[str, Any],
    max_tokens: int = 600,
) -> tuple[str, bool]:
    """
    Returns (response_text, is_ai_generated).
    Falls back to deterministic text when LLM is unavailable.
    """
    settings = get_settings()
    client = _client()

    if client is None:
        logger.info("LLM unavailable — using deterministic fallback")
        return _fallback(prompt, context), False

    try:
        full_prompt = f"{prompt}\n\nDATA:\n{_compact_context(context)}"
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
            timeout=15,
        )
        text = response.choices[0].message.content or ""
        return text.strip(), True
    except Exception as exc:
        logger.warning("LLM call failed: %s — using fallback", exc)
        return _fallback(prompt, context), False


def _compact_context(ctx: dict) -> str:
    import json
    try:
        return json.dumps(ctx, default=str, ensure_ascii=False, indent=None)[:2000]
    except Exception:
        return str(ctx)[:2000]


def _fallback(prompt: str, context: dict) -> str:
    """Deterministic fallback — uses context data to generate a useful response."""
    prompt_lower = prompt.lower()

    # Career advice fallback
    if "career" in prompt_lower or "next" in prompt_lower or "learn" in prompt_lower:
        emp_score = context.get("employability_score", 0)
        missing = context.get("missing_skills", [])
        target = context.get("target_role", "your target role")
        skills_str = ", ".join(missing[:3]) if missing else "cloud and DevOps skills"
        return (
            f"[Deterministic — AI unavailable] "
            f"Based on your profile data, your employability score is {emp_score}/100. "
            f"For {target}, focus on building: {skills_str}. "
            f"Completing a structured assessment and earning at least one verified certification "
            f"will significantly improve your match score for open roles."
        )

    # District insight fallback
    if "district" in prompt_lower:
        district = context.get("district", "the selected district")
        placement = context.get("placement_rate", "N/A")
        top_demand = context.get("top_demand", "Cloud Computing")
        return (
            f"[Deterministic — AI unavailable] "
            f"{district} has a placement rate of {placement}%. "
            f"The top skill in demand is {top_demand}. "
            f"Closing the skill gap between supply and demand should be the immediate priority."
        )

    # Program insight fallback
    if "program" in prompt_lower or "impact" in prompt_lower:
        program = context.get("program_name", "this program")
        score = context.get("impact_score", "N/A")
        return (
            f"[Deterministic — AI unavailable] "
            f"{program} has an impact score of {score}/100. "
            f"Focus on strengthening employer partnerships to improve placement outcomes."
        )

    # Generic fallback
    return (
        "[Deterministic — AI unavailable] "
        "Your profile shows clear opportunities to improve. "
        "Focus on verified skills, complete relevant assessments, and apply to well-matched roles. "
        "Connect with a training program aligned to the skills most in demand in your district."
    )
