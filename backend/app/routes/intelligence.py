from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.auth.dependencies import get_current_user, get_optional_user
from app.database.connection import get_db
from app.services.employability import calculate_employability
from app.services.skill_gap import analyze_skill_gap
from app.schemas.intelligence import SkillGapAnalyzeRequest
from app.analytics.skill_demand import get_skill_demand, get_skill_demand_detail
from app.analytics.forecasting import get_skill_forecast
from app.analytics.district_intelligence import (
    list_districts, get_district, get_district_digital_twin
)
from app.analytics.program_impact import get_program_impact, list_program_impacts

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Intelligence"])


# ── Employability ─────────────────────────────────────────────────────────────

@router.get("/intelligence/employability/me")
async def employability_me(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await calculate_employability(str(user["_id"]), db)


# ── Skill Gap ─────────────────────────────────────────────────────────────────

@router.get("/intelligence/skill-gap/me")
async def skill_gap_me(
    target_role: str = Query(default=""),
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    profile = await db.trainee_profiles.find_one({"user_id": str(user["_id"])})
    role = target_role or (profile or {}).get("target_career", "Cloud Engineer")
    return await analyze_skill_gap(str(user["_id"]), role, db)


@router.post("/intelligence/skill-gap/analyze")
async def skill_gap_analyze(
    body: SkillGapAnalyzeRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await analyze_skill_gap(str(user["_id"]), body.target_role, db, body.target_skills)


# ── Skill Demand ──────────────────────────────────────────────────────────────

@router.get("/intelligence/skill-demand")
async def skill_demand_list(
    industry: str = Query(default=""),
    district: str = Query(default=""),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await get_skill_demand(db, industry or None, district or None)


@router.get("/intelligence/skill-demand/{skill_id}")
async def skill_demand_detail(
    skill_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await get_skill_demand_detail(skill_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Skill demand data not found")
    return result


# ── Forecast ──────────────────────────────────────────────────────────────────

@router.get("/intelligence/forecast")
async def forecast(db: AsyncIOMotorDatabase = Depends(get_db)):
    return await get_skill_forecast(db)


# ── Districts ─────────────────────────────────────────────────────────────────

@router.get("/intelligence/districts")
async def districts(db: AsyncIOMotorDatabase = Depends(get_db)):
    return await list_districts(db)


@router.get("/intelligence/districts/{district_name}")
async def district_detail(
    district_name: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await get_district(district_name, db)
    if not result:
        raise HTTPException(status_code=404, detail="District not found")
    return result


@router.get("/intelligence/districts/{district_name}/digital-twin")
async def district_digital_twin(
    district_name: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await get_district_digital_twin(district_name, db)


# ── Program Impact ────────────────────────────────────────────────────────────

@router.get("/intelligence/program-impact")
async def program_impact_list(db: AsyncIOMotorDatabase = Depends(get_db)):
    return await list_program_impacts(db)


@router.get("/intelligence/program-impact/{program_id}")
async def program_impact_detail(
    program_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await get_program_impact(program_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Program not found")
    return result
