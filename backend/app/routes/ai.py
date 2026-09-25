from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.schemas.ai import (
    CareerAdviceRequest, ChatRequest,
    SkillGapExplainRequest, DistrictInsightRequest, ProgramInsightRequest,
)
from app.ai.llm_service import generate
from app.services.employability import calculate_employability
from app.services.skill_gap import analyze_skill_gap
from app.analytics.district_intelligence import get_district
from app.analytics.program_impact import get_program_impact
from app.utils.serializer import serialize_doc, serialize_docs
from app.models.base import utcnow

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI"])


async def _build_trainee_context(trainee_id: str, db: AsyncIOMotorDatabase) -> dict:
    profile = await db.trainee_profiles.find_one({"user_id": trainee_id}) or {}
    skills_cursor = db.user_skills.find({"user_id": trainee_id})
    skills = await skills_cursor.to_list(length=20)
    emp = await calculate_employability(trainee_id, db)
    target_role = profile.get("target_career", "Cloud Engineer")
    gap = await analyze_skill_gap(trainee_id, target_role, db)

    return {
        "name": profile.get("name", ""),
        "district": profile.get("district", ""),
        "education": profile.get("education", ""),
        "experience": profile.get("experience", ""),
        "target_role": target_role,
        "employment_status": profile.get("employment_status", ""),
        "employability_score": emp["score"],
        "employability_class": emp["classification"],
        "skills": [
            {"skill": s.get("skill_name", ""), "proficiency": s.get("proficiency", 0),
             "verified": s.get("verified", False)}
            for s in skills[:10]
        ],
        "missing_skills": gap.get("missing_skills", []),
        "priority_skills": gap.get("priority_skills", []),
        "overall_match": gap.get("overall_match", 0),
    }


@router.post("/career-advice")
async def career_advice(
    body: CareerAdviceRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Matches the existing /api/assistant/career-advice contract."""
    trainee_id = body.trainee_id
    # Find by user_id
    profile = await db.trainee_profiles.find_one({"user_id": trainee_id})
    if not profile:
        # Fallback to demo trainee
        profile = await db.trainee_profiles.find_one({}) or {}
        if profile:
            trainee_id = profile.get("user_id", trainee_id)

    ctx = await _build_trainee_context(trainee_id, db)
    prompt = (
        f"The trainee asks: \"{body.question}\"\n"
        f"Provide practical career guidance based solely on the provided profile data. "
        f"Be specific, actionable, and reference the actual skills and scores."
    )
    answer, is_ai = await generate(prompt, ctx)

    # Build next steps from gap data
    gap = await analyze_skill_gap(trainee_id, ctx.get("target_role", "Cloud Engineer"), db)
    next_steps = [f"Build {s}" for s in gap.get("priority_skills", [])[:3]]
    if not next_steps:
        next_steps = ["Complete a skills assessment", "Apply to a matching role", "Enroll in a training program"]

    return {
        "answer": answer,
        "sources": ["Your skill profile", f"{ctx['district']} district demand", "KAUSHALYA intelligence model"],
        "nextSteps": next_steps,
        "isAiGenerated": is_ai,
    }


@router.post("/explain-skill-gap")
async def explain_skill_gap(
    body: SkillGapExplainRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    gap = await analyze_skill_gap(user_id, body.target_role, db)
    ctx = {**gap, "target_role": body.target_role}
    prompt = (
        f"Explain WHY the skill gaps for {body.target_role} matter and provide a recommended "
        f"learning sequence for the missing and weak skills. Use only the provided gap data."
    )
    text, is_ai = await generate(prompt, ctx)
    return {"explanation": text, "gap_data": gap, "is_ai_generated": is_ai}


@router.post("/district-insight")
async def district_insight(
    body: DistrictInsightRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    district = await get_district(body.district, db)
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    ctx = {
        "district": district.get("district", ""),
        "placement_rate": district.get("placementRate", 0),
        "top_demand": district.get("topDemand", ""),
        "skill_gap": district.get("skillGap", ""),
        "growth_rate": district.get("growthRate", 0),
        "recommendation": district.get("recommendation", ""),
    }
    prompt = (
        "Provide a concise government-facing intelligence summary for this district. "
        "Include: current situation, key skill gap, future risk, and one concrete recommendation. "
        "Use only the supplied data."
    )
    text, is_ai = await generate(prompt, ctx, max_tokens=400)
    return {
        "summary": text,
        "district_data": district,
        "is_ai_generated": is_ai,
    }


@router.post("/program-insight")
async def program_insight(
    body: ProgramInsightRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    impact = await get_program_impact(body.program_id, db)
    if not impact:
        raise HTTPException(status_code=404, detail="Program not found")
    prompt = (
        "Explain this training program's performance in plain language. "
        "Highlight key strengths, areas to improve, and one specific recommendation. "
        "Use only the supplied metrics."
    )
    text, is_ai = await generate(prompt, impact, max_tokens=350)
    return {"explanation": text, "impact_data": impact, "is_ai_generated": is_ai}


@router.post("/chat")
async def chat(
    body: ChatRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    ctx = await _build_trainee_context(user_id, db)
    prompt = (
        f"User message: \"{body.message}\"\n"
        f"Respond as the KAUSHALYA career assistant. "
        f"Be concise, practical, and reference the user's actual data."
    )
    answer, is_ai = await generate(prompt, ctx)

    # Store conversation
    conv_id = body.conversation_id
    now = utcnow()
    if conv_id:
        await db.ai_conversations.update_one(
            {"_id": ObjectId(conv_id)} if ObjectId.is_valid(str(conv_id or "")) else {"_id": conv_id},
            {"$push": {
                "messages": [
                    {"role": "user", "content": body.message, "timestamp": now},
                    {"role": "assistant", "content": answer, "timestamp": now},
                ]
            }, "$set": {"updated_at": now}},
        )
    else:
        result = await db.ai_conversations.insert_one({
            "user_id": user_id,
            "messages": [
                {"role": "user", "content": body.message, "timestamp": now},
                {"role": "assistant", "content": answer, "timestamp": now},
            ],
            "created_at": now,
            "updated_at": now,
        })
        conv_id = str(result.inserted_id)

    return {"message": answer, "conversation_id": conv_id, "is_ai_generated": is_ai}


@router.get("/conversations")
async def list_conversations(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    cursor = db.ai_conversations.find({"user_id": user_id}).sort("updated_at", -1).limit(20)
    docs = await cursor.to_list(length=20)
    return serialize_docs(docs)


@router.get("/conversations/{conv_id}")
async def get_conversation(
    conv_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await db.ai_conversations.find_one({"_id": ObjectId(conv_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if doc.get("user_id") != str(user["_id"]) and user.get("role") not in ("SUPER_ADMIN",):
        raise HTTPException(status_code=403, detail="Forbidden")
    return serialize_doc(doc)
