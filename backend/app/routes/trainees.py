from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.auth.dependencies import get_current_user, require_role
from app.database.connection import get_db
from app.schemas.trainee import TraineeProfileUpdate, TraineeResponse, TraineeSkillItem
from app.services.employability import calculate_employability, _calc_profile_completion
from app.utils.serializer import serialize_doc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/trainees", tags=["Trainees"])


def _build_trainee_response(profile: dict, skills: list[dict], emp_score: dict) -> dict:
    return {
        "id": profile.get("user_id", ""),
        "name": profile.get("name", ""),
        "email": profile.get("email", ""),
        "phone": profile.get("phone", ""),
        "district": profile.get("district", ""),
        "state": profile.get("state", "Maharashtra"),
        "education": profile.get("education", ""),
        "specialization": profile.get("specialization", ""),
        "employment_status": profile.get("employment_status", "Open to work"),
        "company": profile.get("company"),
        "job_role": profile.get("job_role"),
        "salary": profile.get("salary"),
        "experience": profile.get("experience", ""),
        "profile_completion": _calc_profile_completion(profile),
        "employability_score": emp_score.get("score", 0),
        "score_class": emp_score.get("classification", "Low").capitalize(),
        "target_career": profile.get("target_career", ""),
        "skills": skills,
    }


async def _get_trainee_skills(user_id: str, db: AsyncIOMotorDatabase) -> list[dict]:
    cursor = db.user_skills.find({"user_id": user_id})
    docs = await cursor.to_list(length=100)
    result = []
    for s in docs:
        result.append({
            "skill": s.get("skill_name", ""),
            "skill_id": s.get("skill_id", ""),
            "category": s.get("category", ""),
            "proficiency": s.get("proficiency", 0),
            "level": _proficiency_level(s.get("proficiency", 0)),
            "verified": s.get("verified", False),
            "assessment_score": s.get("assessment_score"),
        })
    return result


def _proficiency_level(score: int) -> str:
    if score >= 86: return "Expert"
    if score >= 71: return "Advanced"
    if score >= 51: return "Intermediate"
    if score >= 31: return "Basic"
    return "Beginner"


@router.get("/me")
async def get_my_profile(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    profile = await db.trainee_profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Trainee profile not found")
    skills = await _get_trainee_skills(user_id, db)
    emp = await calculate_employability(user_id, db)
    return _build_trainee_response(profile, skills, emp)


@router.put("/me")
async def update_my_profile(
    body: TraineeProfileUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    from app.models.base import utcnow
    update["updated_at"] = utcnow()
    await db.trainee_profiles.update_one({"user_id": user_id}, {"$set": update})
    return await get_my_profile(user, db)


@router.get("/{trainee_id}")
async def get_trainee(
    trainee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    profile = await db.trainee_profiles.find_one({"user_id": trainee_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Trainee not found")
    skills = await _get_trainee_skills(trainee_id, db)
    emp = await calculate_employability(trainee_id, db)
    return _build_trainee_response(profile, skills, emp)


@router.patch("/{trainee_id}")
async def patch_trainee(
    trainee_id: str,
    body: TraineeProfileUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    # Allow self-update or admin
    if str(user["_id"]) != trainee_id and user.get("role") not in ("GOVERNMENT_ADMIN", "SUPER_ADMIN"):
        raise HTTPException(status_code=403, detail="Forbidden")
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    from app.models.base import utcnow
    update["updated_at"] = utcnow()
    await db.trainee_profiles.update_one({"user_id": trainee_id}, {"$set": update})
    return await get_trainee(trainee_id, db)
