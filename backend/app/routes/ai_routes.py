from __future__ import annotations
"""
AI routes — all /api/ai/* endpoints.
Each endpoint is authenticated and pulls real user context from MongoDB.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.ai.gemini_client import is_available, get_model_name, llm_status
from app.ai.chatbot import process_chat
from app.ai.career_advisor import get_career_advice
from app.ai.skill_gap_advisor import explain_skill_gap
from app.ai.district_advisor import get_district_insight
from app.ai.program_advisor import get_program_insight
from app.utils.serializer import serialize_doc, serialize_docs

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class SkillGapExplainRequest(BaseModel):
    target_role: str | None = None


class DistrictInsightRequest(BaseModel):
    district: str


class ProgramInsightRequest(BaseModel):
    program_id: str


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health")
async def ai_health(db: AsyncIOMotorDatabase = Depends(get_db)):
    from app.database.connection import check_db_health
    from app.ai.gemini_client import llm_status, embeddings_available

    db_ok = await check_db_health()
    status = llm_status()
    emb_ok = embeddings_available()

    kb_count = 0
    try:
        kb_count = await db.knowledge_base.count_documents({})
    except Exception:
        pass

    return {
        "gemini": status["gemini"],
        "groq": status["groq"],
        "active_llm": status["active"],
        "model": status["model"],
        "mongodb": "connected" if db_ok else "disconnected",
        "embeddings": "available" if emb_ok else "unavailable",
        "knowledge_base_docs": kb_count,
        "fallback_mode": status["fallback_mode"],
    }


# ── Chat ──────────────────────────────────────────────────────────────────────

@router.post("/chat")
async def chat(
    body: ChatRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if len(body.message) > 4000:
        raise HTTPException(status_code=400, detail="Message too long (max 4000 chars)")

    result = await process_chat(
        message=body.message,
        user=user,
        db=db,
        conversation_id=body.conversation_id,
    )
    return {
        "success": True,
        "data": {
            "message": result["answer"],
            "conversation_id": result["conversation_id"],
            "intent": result["intent"],
            "is_ai_generated": result["is_ai_generated"],
            "sources": result.get("sources", []),
            "context_used": result.get("context_used", False),
        },
    }


# ── Conversations ─────────────────────────────────────────────────────────────

@router.get("/conversations")
async def list_conversations(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    cursor = db.ai_conversations.find({"user_id": user_id}).sort("updated_at", -1).limit(20)
    docs = await cursor.to_list(length=20)
    result = []
    for d in docs:
        r = serialize_doc(d) or {}
        # Return only last message for list view
        msgs = r.get("messages", [])
        r["last_message"] = msgs[-1] if msgs else None
        r["message_count"] = len(msgs)
        r.pop("messages", None)
        result.append(r)
    return {"success": True, "data": result}


@router.get("/conversations/{conv_id}")
async def get_conversation(
    conv_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not ObjectId.is_valid(conv_id):
        raise HTTPException(status_code=404, detail="Invalid conversation ID")
    doc = await db.ai_conversations.find_one({"_id": ObjectId(conv_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if doc.get("user_id") != str(user["_id"]) and user.get("role") not in ("SUPER_ADMIN",):
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"success": True, "data": serialize_doc(doc)}


@router.delete("/conversations/{conv_id}", status_code=204)
async def delete_conversation(
    conv_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not ObjectId.is_valid(conv_id):
        raise HTTPException(status_code=404, detail="Invalid conversation ID")
    doc = await db.ai_conversations.find_one({"_id": ObjectId(conv_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if doc.get("user_id") != str(user["_id"]) and user.get("role") not in ("SUPER_ADMIN",):
        raise HTTPException(status_code=403, detail="Forbidden")
    await db.ai_conversations.delete_one({"_id": ObjectId(conv_id)})


# ── Career Advice ─────────────────────────────────────────────────────────────

@router.post("/career-advice")
async def career_advice_endpoint(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    result = await get_career_advice(user_id, db)
    return {"success": True, "data": result}


# ── Skill Gap Explanation ─────────────────────────────────────────────────────

@router.post("/skill-gap-explanation")
async def skill_gap_explanation(
    body: SkillGapExplainRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    profile = await db.trainee_profiles.find_one({"user_id": user_id}) or {}
    target_role = body.target_role or profile.get("target_career", "Cloud Engineer")
    result = await explain_skill_gap(user_id, target_role, db)
    return {"success": True, "data": result}


# ── Job Explanation ───────────────────────────────────────────────────────────

@router.post("/job-explanation")
async def job_explanation(
    job_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.services.job_matching import get_job_matches
    from app.ai.context_builder import build_trainee_context, format_profile_for_prompt
    from app.ai.prompts import JOB_MATCH_ADVISOR

    user_id = str(user["_id"])

    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=404, detail="Invalid job ID")
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    ctx = await build_trainee_context(user_id, db)
    matches = await get_job_matches(user_id, db)
    matched = next((m for m in matches if m.get("id") == job_id or str(job.get("_id", "")) in m.get("id", "")), None)

    match_score = matched.get("match", 0) if matched else 0
    matching = matched.get("matching_skills", []) if matched else []
    missing = matched.get("missing_skills", []) if matched else []

    job_details = (
        f"Title: {job.get('title','')}\n"
        f"Company: {job.get('company','')}\n"
        f"Required Skills: {', '.join(job.get('required_skills', job.get('requiredSkills', [])))}\n"
        f"Experience: {job.get('experience','')}\n"
        f"Location: {job.get('location','')}"
    )

    if is_available():
        from app.ai.gemini_client import generate_text
        prompt = JOB_MATCH_ADVISOR.format(
            system=KAUSHALYA_SYSTEM_IMPORT(),
            profile=format_profile_for_prompt(ctx),
            job_details=job_details,
            match_score=match_score,
            matching_skills=", ".join(matching) or "None",
            missing_skills=", ".join(missing) or "None",
        )
        answer, is_ai = await generate_text(prompt, max_output_tokens=600)
        if answer:
            return {"success": True, "data": {
                "explanation": answer, "match_score": match_score,
                "matching_skills": matching, "missing_skills": missing,
                "is_ai_generated": is_ai,
            }}

    explanation = (
        f"Job Match Analysis for {job.get('title','this role')}:\n"
        f"• Match Score: {match_score}%\n"
        f"• Matching Skills: {', '.join(matching) or 'None'}\n"
        f"• Missing Skills: {', '.join(missing) or 'None'}\n"
        "[AI unavailable — showing calculated match data]"
    )
    return {"success": True, "data": {
        "explanation": explanation, "match_score": match_score,
        "matching_skills": matching, "missing_skills": missing,
        "is_ai_generated": False,
    }}


def KAUSHALYA_SYSTEM_IMPORT():
    from app.ai.prompts import KAUSHALYA_SYSTEM
    return KAUSHALYA_SYSTEM


# ── Training Recommendation ───────────────────────────────────────────────────

@router.post("/training-recommendation")
async def training_recommendation(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.ai.context_builder import build_trainee_context, format_skill_gaps_for_prompt
    from app.ai.prompts import TRAINING_ADVISOR, KAUSHALYA_SYSTEM
    from app.services.skill_gap import analyze_skill_gap
    from app.ai.gemini_client import generate_text

    user_id = str(user["_id"])
    profile = await db.trainee_profiles.find_one({"user_id": user_id}) or {}
    target = profile.get("target_career", "Cloud Engineer")
    gap = await analyze_skill_gap(user_id, target, db)

    programs_cursor = db.training_programs.find().sort("placement_rate", -1).limit(6)
    programs_docs = await programs_cursor.to_list(length=6)
    programs_text = "\n".join(
        f"- {p.get('name','')} ({p.get('location','')}, {p.get('duration','')}): "
        f"{p.get('placement_rate',0)}% placement | Skills: {', '.join(p.get('skills',[])[:4])}"
        for p in programs_docs
    ) or "No programs available."

    gap_text = format_skill_gaps_for_prompt(gap)

    if is_available():
        prompt = TRAINING_ADVISOR.format(
            system=KAUSHALYA_SYSTEM,
            skill_gaps=gap_text,
            target_career=target,
            programs=programs_text,
        )
        answer, is_ai = await generate_text(prompt, max_output_tokens=700)
        if answer:
            return {"success": True, "data": {"recommendation": answer, "is_ai_generated": is_ai, "programs": programs_docs[:3]}}

    rec_names = gap.get("recommended_training", [])
    answer = (
        f"Based on your skill gaps for {target}:\n"
        f"• Priority skills needed: {', '.join(gap.get('priority_skills',[])[:3])}\n"
        f"• Recommended programs: {', '.join(rec_names[:2]) if rec_names else 'See training page'}\n"
        "[AI unavailable — showing gap-based recommendations]"
    )
    return {"success": True, "data": {"recommendation": answer, "is_ai_generated": False, "programs": programs_docs[:3]}}


# ── District Insight ──────────────────────────────────────────────────────────

@router.post("/district-insight")
async def district_insight(
    body: DistrictInsightRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await get_district_insight(body.district, db)
    return {"success": True, "data": result}


# ── Program Insight ───────────────────────────────────────────────────────────

@router.post("/program-insight")
async def program_insight(
    body: ProgramInsightRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await get_program_insight(body.program_id, db)
    return {"success": True, "data": result}


# ── Compat: /assistant/career-advice (existing frontend hook) ─────────────────

class LegacyCareerRequest(BaseModel):
    traineeId: str
    question: str


@router.post("/legacy-career-advice", include_in_schema=False)
async def legacy_career_advice(body: LegacyCareerRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Internal compat — called by compat router at /assistant/career-advice."""
    from app.ai.chatbot import process_chat
    from app.ai.context_builder import build_trainee_context

    profile = await db.trainee_profiles.find_one({"user_id": body.traineeId}) or {}
    user = await db.users.find_one({"email": profile.get("email", "")}) or {
        "_id": __import__("bson").ObjectId(),
        "role": "TRAINEE",
        "name": profile.get("name", "Trainee"),
    }
    result = await process_chat(body.question, user, db)
    return {
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "nextSteps": [],
        "isAiGenerated": result["is_ai_generated"],
    }
