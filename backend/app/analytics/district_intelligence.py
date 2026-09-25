from __future__ import annotations
"""
District Intelligence — aggregates from MongoDB district_data and employment_outcomes.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase


async def list_districts(db: AsyncIOMotorDatabase) -> list[dict]:
    cursor = db.district_data.find().sort("placement_rate", -1)
    docs = await cursor.to_list(length=20)
    return [_serialize_district(d) for d in docs]


async def get_district(district_name: str, db: AsyncIOMotorDatabase) -> dict | None:
    doc = await db.district_data.find_one(
        {"district": {"$regex": f"^{district_name}$", "$options": "i"}}
    )
    if not doc:
        return None
    return _serialize_district(doc)


async def get_district_digital_twin(district_name: str, db: AsyncIOMotorDatabase) -> dict:
    doc = await db.district_data.find_one(
        {"district": {"$regex": f"^{district_name}$", "$options": "i"}}
    )
    if not doc:
        return {"error": "District not found"}

    trainees = doc.get("trainees", 0)
    employed = doc.get("employed", 0)
    placement_rate = doc.get("placement_rate", 0)

    # Aggregate employment outcomes for this district
    pipeline = [
        {"$match": {"location": {"$regex": district_name, "$options": "i"}}},
        {"$group": {
            "_id": None,
            "avg_salary": {"$avg": "$salary"},
            "count": {"$sum": 1},
            "retention_6m": {"$sum": {"$cond": ["$retention_6_months", 1, 0]}},
        }},
    ]
    agg = await db.employment_outcomes.aggregate(pipeline).to_list(length=1)
    outcome_agg = agg[0] if agg else {}

    return {
        "district": doc.get("district", ""),
        "workforce": {
            "total_trainees": trainees,
            "employed": employed,
            "unemployed": trainees - employed,
            "placement_rate": placement_rate,
        },
        "skills": {
            "top_demand": doc.get("top_demand", ""),
            "top_available": doc.get("top_available", ""),
            "skill_supply": doc.get("skill_supply", ""),
            "skill_demand": doc.get("skill_demand", ""),
            "skill_gap": doc.get("skill_gap", ""),
        },
        "training": {
            "programs_available": await db.training_programs.count_documents(
                {"location": {"$regex": district_name, "$options": "i"}}
            ),
        },
        "employment": {
            "average_salary": doc.get("average_salary", ""),
            "avg_salary_numeric": round(outcome_agg.get("avg_salary") or 0, 2),
            "outcomes_recorded": outcome_agg.get("count", 0),
            "retention_6m_count": outcome_agg.get("retention_6m", 0),
        },
        "industry_demand": {
            "top_industry": doc.get("top_demand", ""),
            "growth_rate": doc.get("growth_rate", 0),
        },
        "skill_gaps": {
            "top_gap": doc.get("top_demand", ""),
            "skill_gap_score": _gap_score(doc),
            "classification": doc.get("status", "yellow").upper(),
        },
        "forecast": {
            "future_demand": doc.get("future_demand", ""),
            "growth_rate": doc.get("growth_rate", 0),
        },
        "recommendations": [doc.get("recommendation", "")],
    }


def _serialize_district(doc: dict) -> dict:
    return {
        "district": doc.get("district", ""),
        "region": doc.get("region", ""),
        "status": doc.get("status", "yellow"),
        "trainees": doc.get("trainees", 0),
        "employed": doc.get("employed", 0),
        "placementRate": doc.get("placement_rate", 0),
        "averageSalary": doc.get("average_salary", ""),
        "skillSupply": doc.get("skill_supply", ""),
        "skillDemand": doc.get("skill_demand", ""),
        "skillGap": doc.get("skill_gap", ""),
        "topDemand": doc.get("top_demand", ""),
        "topAvailable": doc.get("top_available", ""),
        "futureDemand": doc.get("future_demand", ""),
        "growthRate": doc.get("growth_rate", 0),
        "recommendation": doc.get("recommendation", ""),
        "coordinates": doc.get("coordinates", {"x": 0, "y": 0}),
    }


def _gap_score(doc: dict) -> int:
    """Return a 0-100 gap score based on status."""
    status_map = {"green": 15, "yellow": 35, "orange": 60, "red": 85}
    return status_map.get(doc.get("status", "yellow"), 35)
