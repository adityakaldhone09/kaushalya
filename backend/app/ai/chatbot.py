from __future__ import annotations
"""
Core chatbot — intent routing, context building, Gemini call, fallback.
"""
import logging
import time
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from .gemini_client import generate_text, is_available, get_model_name
from .prompts import (
    KAUSHALYA_SYSTEM, INTENT_ROUTER, CAREER_ADVISOR, SKILL_GAP_ADVISOR,
    TRAINING_ADVISOR, DISTRICT_INSIGHT, PROGRAM_INSIGHT, GENERAL_KAUSHALYA,
    FALLBACK_TEMPLATES,
)
from .context_builder import (
    build_trainee_context, build_government_context,
    format_profile_for_prompt, format_skill_gaps_for_prompt,
)

logger = logging.getLogger(__name__)

# Intent → routing
_CAREER_KEYWORDS = {"career", "become", "job", "role", "path", "future", "goal", "profession"}
_SKILL_KEYWORDS = {"learn", "skill", "missing", "gap", "study", "improve", "lacking", "need"}
_TRAINING_KEYWORDS = {"course", "program", "training", "enroll", "bootcamp", "certification"}
_JOB_KEYWORDS = {"job", "match", "apply", "opening", "vacancy", "hiring", "work"}
_DISTRICT_KEYWORDS = {"district", "region", "pune", "mumbai", "nagpur", "nashik", "thane", "maharashtra"}
_DEMAND_KEYWORDS = {"demand", "market", "trending", "industry", "growing", "popular", "hot"}
_PROGRAM_KEYWORDS = {"placement", "completion", "impact", "performance", "institute", "results"}


def _detect_intent(message: str) -> str:
    msg = message.lower()
    if any(k in msg for k in _DISTRICT_KEYWORDS):
        return "DISTRICT_INTELLIGENCE"
    if any(k in msg for k in _PROGRAM_KEYWORDS):
        return "PROGRAM_IMPACT"
    if any(k in msg for k in _TRAINING_KEYWORDS):
        return "TRAINING_RECOMMENDATION"
    if any(k in msg for k in _SKILL_KEYWORDS):
        return "SKILL_GAP"
    if any(k in msg for k in _JOB_KEYWORDS):
        return "JOB_RECOMMENDATION"
    if any(k in msg for k in _DEMAND_KEYWORDS):
        return "SKILL_DEMAND"
    if any(k in msg for k in _CAREER_KEYWORDS):
        return "CAREER_ADVICE"
    return "GENERAL_KAUSHALYA"


def _sanitize(text: str, max_len: int = 4000) -> str:
    """Truncate and strip prompt-injection attempts."""
    stripped = text.strip()[:max_len]
    # Block obvious injection patterns
    injections = ["ignore previous", "ignore all", "system prompt", "api key",
                  "credentials", "show password", "forget everything"]
    lower = stripped.lower()
    if any(p in lower for p in injections):
        return "Please ask a question about careers, skills, or workforce development."
    return stripped


async def _get_trainee_skill_gap(user_id: str, db: AsyncIOMotorDatabase) -> dict:
    """Pull skill gap from existing service."""
    try:
        from app.services.skill_gap import analyze_skill_gap
        profile = await db.trainee_profiles.find_one({"user_id": user_id}) or {}
        target = profile.get("target_career", "Cloud Engineer")
        return await analyze_skill_gap(user_id, target, db)
    except Exception as exc:
        logger.warning("Skill gap fetch failed: %s", exc)
        return {}


async def _get_training_programs(db: AsyncIOMotorDatabase, limit: int = 6) -> list[dict]:
    cursor = db.training_programs.find().sort("placement_rate", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [
        {
            "name": d.get("name", ""),
            "location": d.get("location", ""),
            "duration": d.get("duration", ""),
            "placement_rate": d.get("placement_rate", 0),
            "skills": d.get("skills", [])[:4],
        }
        for d in docs
    ]


def _programs_to_text(programs: list[dict]) -> str:
    lines = []
    for p in programs:
        skills = ", ".join(p.get("skills", []))
        lines.append(f"- {p['name']} ({p.get('location','')}, {p.get('duration','')}): "
                     f"{p.get('placement_rate',0)}% placement | Skills: {skills}")
    return "\n".join(lines) if lines else "No programs available."


async def _build_prompt_for_intent(
    intent: str,
    message: str,
    user: dict,
    db: AsyncIOMotorDatabase,
) -> str:
    role = user.get("role", "TRAINEE")
    user_id = str(user["_id"])

    if intent in ("CAREER_ADVICE", "SKILL_GAP", "JOB_RECOMMENDATION",
                  "TRAINING_RECOMMENDATION", "PROFILE_HELP") and role == "TRAINEE":
        ctx = await build_trainee_context(user_id, db)
        gap = await _get_trainee_skill_gap(user_id, db)
        programs = await _get_training_programs(db)

        profile_text = format_profile_for_prompt(ctx)
        gap_text = format_skill_gaps_for_prompt(gap) if gap else "Gap data unavailable."
        programs_text = _programs_to_text(programs)

        if intent == "SKILL_GAP":
            return SKILL_GAP_ADVISOR.format(
                system=KAUSHALYA_SYSTEM,
                profile=profile_text,
                skill_gap_data=gap_text,
                target_role=ctx.get("target_career", "your target role"),
            )
        if intent == "TRAINING_RECOMMENDATION":
            return TRAINING_ADVISOR.format(
                system=KAUSHALYA_SYSTEM,
                skill_gaps=gap_text,
                target_career=ctx.get("target_career", ""),
                programs=programs_text,
            )
        # CAREER_ADVICE, JOB_RECOMMENDATION, PROFILE_HELP
        jobs_cursor = db.jobs.find({"status": "open"}).limit(4)
        jobs_docs = await jobs_cursor.to_list(length=4)
        jobs_text = "\n".join(
            f"- {j.get('title','')} at {j.get('company','')} ({j.get('location','')}): {', '.join(j.get('required_skills',[])[:3])}"
            for j in jobs_docs
        ) or "No jobs available."

        return CAREER_ADVISOR.format(
            system=KAUSHALYA_SYSTEM,
            profile=profile_text,
            skill_gaps=gap_text,
            employability_score=ctx.get("employability_score", 0),
            jobs=jobs_text,
            training=programs_text,
            question=message,
        )

    if intent == "DISTRICT_INTELLIGENCE":
        # Extract district name from message or use all
        import re
        districts = ["Pune", "Mumbai", "Nagpur", "Nashik", "Thane", "Navi Mumbai",
                     "Kolhapur", "Solapur", "Amravati", "Chhatrapati Sambhajinagar"]
        found = next((d for d in districts if d.lower() in message.lower()), "Maharashtra")

        doc = await db.district_data.find_one(
            {"district": {"$regex": f"^{found}$", "$options": "i"}}
        ) or {}
        demand_cursor = db.skill_demand.find({"location": {"$regex": found, "$options": "i"}}).sort("current_demand", -1).limit(5)
        demand_docs = await demand_cursor.to_list(length=5)

        workforce = (
            f"Trainees: {doc.get('trainees', 'N/A')}\n"
            f"Employed: {doc.get('employed', 'N/A')}\n"
            f"Placement Rate: {doc.get('placement_rate', 'N/A')}%\n"
            f"Average Salary: {doc.get('average_salary', 'N/A')}\n"
            f"Skill Gap Status: {doc.get('skill_gap', 'N/A')}\n"
            f"Recommendation: {doc.get('recommendation', 'N/A')}"
        )
        demand_text = "\n".join(
            f"- {d.get('skill_name','')}: demand={d.get('current_demand',0)}, growth=+{d.get('growth_rate',0)}%"
            for d in demand_docs
        ) or "No demand data."

        training_cursor = db.training_programs.find({"location": {"$regex": found, "$options": "i"}}).limit(3)
        training_docs = await training_cursor.to_list(length=3)
        training_text = "\n".join(
            f"- {p.get('name','')}: {p.get('placement_rate',0)}% placement"
            for p in training_docs
        ) or "No programs in this district."

        return DISTRICT_INSIGHT.format(
            system=KAUSHALYA_SYSTEM,
            district=found,
            workforce_data=workforce,
            skill_demand=demand_text,
            training_data=training_text,
        )

    if intent == "PROGRAM_IMPACT":
        cursor = db.training_programs.find().sort("placement_rate", -1).limit(5)
        programs = await cursor.to_list(length=5)
        programs_text = "\n".join(
            f"- {p.get('name','')}: placement={p.get('placement_rate',0)}%, "
            f"completion={p.get('completion_rate',0)}%, impact={p.get('impact_score',0)}"
            for p in programs
        ) or "No program data."
        return PROGRAM_INSIGHT.format(
            system=KAUSHALYA_SYSTEM,
            program_name="Top Programs",
            institute="Various",
            placement_rate="See list",
            completion_rate="See list",
            impact_score="See list",
            avg_salary="See data",
            retention_rate="See data",
        ) + f"\n\nPROGRAMS:\n{programs_text}\n\nUSER QUESTION: {message}"

    if intent == "SKILL_DEMAND":
        cursor = db.skill_demand.find().sort("current_demand", -1).limit(10)
        demand_docs = await cursor.to_list(length=10)
        demand_text = "\n".join(
            f"- {d.get('skill_name','')}: demand={d.get('current_demand',0)}, "
            f"growth=+{d.get('growth_rate',0)}%, location={d.get('location','')}"
            for d in demand_docs
        ) or "No demand data."
        return f"{KAUSHALYA_SYSTEM}\n\nSKILL DEMAND DATA:\n{demand_text}\n\nUSER QUESTION: {message}"

    # GENERAL / fallback
    knowledge_cursor = db.knowledge_base.find(
        {"$text": {"$search": message}}
    ).limit(3)
    try:
        knowledge_docs = await knowledge_cursor.to_list(length=3)
    except Exception:
        knowledge_docs = []
    knowledge_text = "\n\n".join(
        f"[{d.get('title','')}]\n{d.get('content','')[:400]}"
        for d in knowledge_docs
    ) or "No specific knowledge found."

    return GENERAL_KAUSHALYA.format(
        system=KAUSHALYA_SYSTEM,
        knowledge=knowledge_text,
        question=message,
    )


def _deterministic_fallback(intent: str, user: dict, extra: dict) -> str:
    """Return a useful answer when Gemini is unavailable."""
    role = user.get("role", "TRAINEE")
    name = user.get("name", "")

    if intent == "CAREER_ADVICE":
        score = extra.get("employability_score", 0)
        priority = ", ".join(extra.get("priority_skills", ["AWS", "Docker"])[:3])
        training = extra.get("recommended_training", "Cloud & DevOps Accelerator")
        return (
            f"Hi {name}! Based on your KAUSHALYA profile:\n\n"
            f"• Employability Score: {score}/100\n"
            f"• Priority skills to build: {priority}\n"
            f"• Recommended program: {training}\n\n"
            "[AI assistance unavailable — showing data-driven recommendations]"
        )
    if intent == "SKILL_GAP":
        missing = ", ".join(extra.get("missing_skills", ["AWS", "Docker"])[:3])
        target = extra.get("target_role", "your target role")
        return (
            f"Your skill gap for {target}:\n"
            f"• Missing skills: {missing}\n"
            f"• Enroll in a relevant training program to close these gaps.\n\n"
            "[AI assistance unavailable — showing calculated gap data]"
        )
    if intent == "DISTRICT_INTELLIGENCE":
        district = extra.get("district", "Maharashtra")
        rate = extra.get("placement_rate", "N/A")
        top = extra.get("top_demand", "Cloud Computing")
        return (
            f"{district} — Placement Rate: {rate}% | Top Demand: {top}\n\n"
            "[AI assistance unavailable — showing database statistics]"
        )
    return (
        "AI assistance is temporarily unavailable. "
        "Please browse the KAUSHALYA dashboards for skill demand, job matches, and training programs."
    )


async def process_chat(
    message: str,
    user: dict,
    db: AsyncIOMotorDatabase,
    conversation_id: str | None = None,
) -> dict:
    """
    Main chat entry point.
    Returns: {answer, intent, conversation_id, sources, context_used, is_ai}
    """
    start = time.time()
    safe_message = _sanitize(message)
    intent = _detect_intent(safe_message)
    user_id = str(user["_id"])
    role = user.get("role", "TRAINEE")

    logger.info("chat user=%s role=%s intent=%s", user_id[:8], role, intent)

    # Build conversation record
    now = datetime.now(timezone.utc)
    user_message = {"role": "user", "content": safe_message, "timestamp": now}

    # Try Gemini
    answer = ""
    is_ai = False

    if is_available():
        try:
            prompt = await _build_prompt_for_intent(intent, safe_message, user, db)
            answer, is_ai = await generate_text(prompt, max_output_tokens=800)
        except Exception as exc:
            logger.warning("Chat Gemini call failed: %s", exc)

    # Fallback if Gemini didn't produce anything
    if not answer:
        extra: dict = {}
        if role == "TRAINEE":
            try:
                ctx = await build_trainee_context(user_id, db)
                gap = await _get_trainee_skill_gap(user_id, db)
                extra = {
                    "employability_score": ctx.get("employability_score", 0),
                    "priority_skills": gap.get("priority_skills", []),
                    "missing_skills": gap.get("missing_skills", []),
                    "target_role": ctx.get("target_career", ""),
                    "recommended_training": (gap.get("recommended_training") or ["a relevant program"])[0],
                }
            except Exception:
                pass
        answer = _deterministic_fallback(intent, user, extra)

    assistant_message = {"role": "assistant", "content": answer, "timestamp": datetime.now(timezone.utc)}

    # Persist / update conversation
    if conversation_id and ObjectId.is_valid(conversation_id):
        await db.ai_conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$push": {"messages": {"$each": [user_message, assistant_message]}},
             "$set": {"updated_at": now}},
        )
    else:
        result = await db.ai_conversations.insert_one({
            "user_id": user_id,
            "intent": intent,
            "messages": [user_message, assistant_message],
            "created_at": now,
            "updated_at": now,
        })
        conversation_id = str(result.inserted_id)

    elapsed = round(time.time() - start, 2)
    logger.info("chat done intent=%s ai=%s elapsed=%ss", intent, is_ai, elapsed)

    return {
        "answer": answer,
        "intent": intent,
        "conversation_id": conversation_id,
        "sources": [],
        "context_used": True,
        "is_ai_generated": is_ai,
        "model": get_model_name() if is_ai else "deterministic",
    }
