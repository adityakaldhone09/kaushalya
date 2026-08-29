from __future__ import annotations
from motor.motor_asyncio import AsyncIOMotorDatabase
from .gemini_client import generate_text, is_available
from .prompts import KAUSHALYA_SYSTEM, SKILL_GAP_ADVISOR
from .context_builder import build_trainee_context, format_profile_for_prompt, format_skill_gaps_for_prompt


async def explain_skill_gap(user_id: str, target_role: str, db: AsyncIOMotorDatabase) -> dict:
    from app.services.skill_gap import analyze_skill_gap

    ctx = await build_trainee_context(user_id, db)
    gap = await analyze_skill_gap(user_id, target_role, db)

    profile_text = format_profile_for_prompt(ctx)
    gap_text = format_skill_gaps_for_prompt(gap)

    if is_available():
        prompt = SKILL_GAP_ADVISOR.format(
            system=KAUSHALYA_SYSTEM,
            profile=profile_text,
            skill_gap_data=gap_text,
            target_role=target_role,
        )
        answer, is_ai = await generate_text(prompt, max_output_tokens=800)
        if answer:
            return {"explanation": answer, "gap_data": gap, "is_ai_generated": is_ai}

    missing = gap.get("missing_skills", [])
    priority = gap.get("priority_skills", [])
    explanation = (
        f"Your skill gap for {target_role}:\n"
        f"• Match: {gap.get('overall_match', 0)}%\n"
        f"• Missing: {', '.join(missing[:5]) if missing else 'None identified'}\n"
        f"• Priority to learn: {', '.join(priority[:3]) if priority else 'N/A'}\n"
        "[AI explanation unavailable — showing calculated gap data]"
    )
    return {"explanation": explanation, "gap_data": gap, "is_ai_generated": False}
