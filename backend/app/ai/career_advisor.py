from __future__ import annotations
from motor.motor_asyncio import AsyncIOMotorDatabase
from .gemini_client import generate_text, is_available
from .prompts import KAUSHALYA_SYSTEM, CAREER_ADVISOR, FALLBACK_TEMPLATES
from .context_builder import build_trainee_context, format_profile_for_prompt, format_skill_gaps_for_prompt


async def get_career_advice(user_id: str, db: AsyncIOMotorDatabase) -> dict:
    from app.services.skill_gap import analyze_skill_gap

    ctx = await build_trainee_context(user_id, db)
    profile = await db.trainee_profiles.find_one({"user_id": user_id}) or {}
    target = profile.get("target_career", "Cloud Engineer")
    gap = await analyze_skill_gap(user_id, target, db)

    # Top jobs
    jobs_cursor = db.jobs.find({"status": "open"}).limit(5)
    jobs_docs = await jobs_cursor.to_list(length=5)
    jobs_text = "\n".join(
        f"- {j.get('title','')} at {j.get('company','')} ({j.get('location','')}): "
        f"{', '.join(j.get('required_skills',[])[:3])}"
        for j in jobs_docs
    ) or "No jobs available."

    # Top programs
    programs_cursor = db.training_programs.find().sort("placement_rate", -1).limit(4)
    programs_docs = await programs_cursor.to_list(length=4)
    programs_text = "\n".join(
        f"- {p.get('name','')} ({p.get('location','')}): {p.get('placement_rate',0)}% placement"
        for p in programs_docs
    ) or "No programs available."

    profile_text = format_profile_for_prompt(ctx)
    gap_text = format_skill_gaps_for_prompt(gap)

    if is_available():
        prompt = CAREER_ADVISOR.format(
            system=KAUSHALYA_SYSTEM,
            profile=profile_text,
            skill_gaps=gap_text,
            employability_score=ctx.get("employability_score", 0),
            jobs=jobs_text,
            training=programs_text,
            question="Give me a comprehensive career recommendation based on my profile.",
        )
        answer, is_ai = await generate_text(prompt, max_output_tokens=1000)
        if answer:
            return {"advice": answer, "is_ai_generated": is_ai, "context": ctx}

    # Fallback
    priority = gap.get("priority_skills", [])[:3]
    training = (gap.get("recommended_training") or [programs_docs[0].get("name", "a program") if programs_docs else "a training program"])[0]
    advice = FALLBACK_TEMPLATES["CAREER_ADVICE"].format(
        score=ctx.get("employability_score", 0),
        priority_skills=", ".join(priority) if priority else "Cloud and DevOps skills",
        recommended_training=training,
    )
    return {"advice": advice, "is_ai_generated": False, "context": ctx}
