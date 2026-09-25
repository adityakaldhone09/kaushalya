from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.schemas.skill import SkillCreate, SkillUpdate, UserSkillCreate, UserSkillUpdate
from app.utils.serializer import serialize_doc, serialize_docs
from app.models.base import utcnow

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Skills"])


def _demand_to_relevance(score: int) -> str:
    if score >= 85: return "Very high"
    if score >= 70: return "High"
    if score >= 50: return "Moderate"
    return "Low"


def _doc_to_skill(doc: dict) -> dict:
    s = serialize_doc(doc) or {}
    s["industry_relevance"] = _demand_to_relevance(s.get("demand_score", 50))
    return s


# ── Taxonomy ──────────────────────────────────────────────────────────────────

@router.get("/skills")
async def list_skills(
    search: str = Query(default=""),
    category: str = Query(default=""),
    industry: str = Query(default=""),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=200),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    q: dict = {}
    if search:
        q["name"] = {"$regex": search, "$options": "i"}
    if category:
        q["category"] = category
    if industry:
        q["industries"] = {"$in": [industry]}

    cursor = db.skills.find(q).skip(skip).limit(limit).sort("demand_score", -1)
    docs = await cursor.to_list(length=limit)
    return [_doc_to_skill(d) for d in docs]


@router.get("/skills/{skill_id}")
async def get_skill(skill_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db.skills.find_one({"_id": ObjectId(skill_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Skill not found")
    return _doc_to_skill(doc)


@router.post("/skills", status_code=201)
async def create_skill(
    body: SkillCreate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if user.get("role") not in ("GOVERNMENT_ADMIN", "SUPER_ADMIN"):
        raise HTTPException(status_code=403, detail="Admin access required")
    existing = await db.skills.find_one({"name": {"$regex": f"^{body.name}$", "$options": "i"}})
    if existing:
        raise HTTPException(status_code=409, detail="Skill already exists")
    doc = {**body.model_dump(), "created_at": utcnow()}
    result = await db.skills.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_skill(doc)


@router.put("/skills/{skill_id}")
async def update_skill(
    skill_id: str,
    body: SkillUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if user.get("role") not in ("GOVERNMENT_ADMIN", "SUPER_ADMIN"):
        raise HTTPException(status_code=403, detail="Admin access required")
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    update["updated_at"] = utcnow()
    result = await db.skills.find_one_and_update(
        {"_id": ObjectId(skill_id)}, {"$set": update}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Skill not found")
    return _doc_to_skill(result)


@router.delete("/skills/{skill_id}", status_code=204)
async def delete_skill(
    skill_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if user.get("role") not in ("SUPER_ADMIN",):
        raise HTTPException(status_code=403, detail="Super admin required")
    await db.skills.delete_one({"_id": ObjectId(skill_id)})


# ── User Skills ───────────────────────────────────────────────────────────────

@router.get("/trainees/me/skills")
async def get_my_skills(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    cursor = db.user_skills.find({"user_id": user_id})
    docs = await cursor.to_list(length=100)
    return serialize_docs(docs)


@router.post("/trainees/me/skills", status_code=201)
async def add_my_skill(
    body: UserSkillCreate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    skill = await db.skills.find_one({"_id": ObjectId(body.skill_id)})
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing = await db.user_skills.find_one({"user_id": user_id, "skill_id": body.skill_id})
    if existing:
        raise HTTPException(status_code=409, detail="Skill already in profile")

    from app.routes.trainees import _proficiency_level
    doc = {
        "user_id": user_id,
        "skill_id": body.skill_id,
        "skill_name": skill["name"],
        "category": skill.get("category", ""),
        "proficiency": body.proficiency,
        "level": _proficiency_level(body.proficiency),
        "verified": False,
        "assessment_score": None,
        "source": body.source,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    result = await db.user_skills.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@router.put("/trainees/me/skills/{skill_id}")
async def update_my_skill(
    skill_id: str,
    body: UserSkillUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    if "proficiency" in update:
        from app.routes.trainees import _proficiency_level
        update["level"] = _proficiency_level(update["proficiency"])
    update["updated_at"] = utcnow()
    result = await db.user_skills.find_one_and_update(
        {"user_id": user_id, "skill_id": skill_id},
        {"$set": update},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="User skill not found")
    return serialize_doc(result)


@router.delete("/trainees/me/skills/{skill_id}", status_code=204)
async def delete_my_skill(
    skill_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    await db.user_skills.delete_one({"user_id": user_id, "skill_id": skill_id})
