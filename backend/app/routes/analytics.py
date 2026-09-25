from __future__ import annotations
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.connection import get_db
from app.analytics.district_intelligence import list_districts
from app.analytics.skill_demand import get_skill_demand
from app.analytics.forecasting import get_skill_forecast

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analytics"])


@router.get("/analytics/government")
async def government_analytics(
    state: str = Query(default="Maharashtra"),
    district: str = Query(default=""),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    total_trainees = await db.trainee_profiles.count_documents({})
    total_employers = await db.employers.count_documents({})
    total_programs = await db.training_programs.count_documents({})

    # Employment rate
    emp_pipeline = [
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "employed": {
                "$sum": {"$cond": [{"$eq": ["$employment_status", "Employed"]}, 1, 0]}
            },
        }},
    ]
    emp_agg = await db.trainee_profiles.aggregate(emp_pipeline).to_list(length=1)
    emp_data = emp_agg[0] if emp_agg else {"total": 1, "employed": 0}
    employment_rate = (
        round(emp_data["employed"] / emp_data["total"] * 100, 1) if emp_data["total"] else 0
    )

    # Avg salary
    salary_pipeline = [
        {"$match": {"salary": {"$exists": True, "$ne": None, "$gt": 0}}},
        {"$group": {"_id": None, "avg": {"$avg": "$salary"}}},
    ]
    sal_agg = await db.employment_outcomes.aggregate(salary_pipeline).to_list(length=1)
    avg_salary = round(sal_agg[0]["avg"], 1) if sal_agg else 4.8

    # Retention
    ret_pipeline = [
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "retained": {"$sum": {"$cond": ["$retention_6_months", 1, 0]}},
        }},
    ]
    ret_agg = await db.employment_outcomes.aggregate(ret_pipeline).to_list(length=1)
    ret_data = ret_agg[0] if ret_agg else {"total": 1, "retained": 0}
    retention_rate = (
        round(ret_data["retained"] / ret_data["total"] * 100, 1) if ret_data["total"] else 78
    )

    return {
        "total_trainees": total_trainees,
        "total_employers": total_employers,
        "total_programs": total_programs,
        "employment_rate": employment_rate,
        "average_salary": avg_salary,
        "retention_rate": retention_rate,
    }


@router.get("/analytics/employment")
async def employment_analytics(
    district: str = Query(default=""),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    match: dict = {}
    if district:
        match["location"] = {"$regex": district, "$options": "i"}

    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "avg_salary": {"$avg": "$salary"},
            "retention_6m": {"$sum": {"$cond": ["$retention_6_months", 1, 0]}},
            "retention_12m": {"$sum": {"$cond": ["$retention_12_months", 1, 0]}},
        }},
    ]
    agg = await db.employment_outcomes.aggregate(pipeline).to_list(length=1)
    data = agg[0] if agg else {}
    total = data.get("total", 0)

    return {
        "total_outcomes": total,
        "average_salary": round(data.get("avg_salary") or 0, 2),
        "retention_6m_rate": round(data.get("retention_6m", 0) / total * 100, 1) if total else 0,
        "retention_12m_rate": round(data.get("retention_12m", 0) / total * 100, 1) if total else 0,
    }


@router.get("/analytics/skills")
async def skills_analytics(db: AsyncIOMotorDatabase = Depends(get_db)):
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}, "avg_demand": {"$avg": "$demand_score"}}},
        {"$sort": {"avg_demand": -1}},
    ]
    agg = await db.skills.aggregate(pipeline).to_list(length=20)
    return [{"category": a["_id"], "count": a["count"], "avg_demand": round(a["avg_demand"], 1)} for a in agg]


@router.get("/analytics/training")
async def training_analytics(db: AsyncIOMotorDatabase = Depends(get_db)):
    pipeline = [
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "avg_placement": {"$avg": "$placement_rate"},
            "avg_completion": {"$avg": "$completion_rate"},
            "total_enrolled": {"$sum": "$enrolled"},
        }},
    ]
    agg = await db.training_programs.aggregate(pipeline).to_list(length=1)
    data = agg[0] if agg else {}
    return {
        "total_programs": data.get("total", 0),
        "avg_placement_rate": round(data.get("avg_placement") or 0, 1),
        "avg_completion_rate": round(data.get("avg_completion") or 0, 1),
        "total_enrolled": data.get("total_enrolled", 0),
    }


@router.get("/analytics/districts")
async def districts_analytics(db: AsyncIOMotorDatabase = Depends(get_db)):
    return await list_districts(db)
