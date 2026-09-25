from __future__ import annotations
"""
Skill Demand Analytics — aggregates from MongoDB.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase


_STATUS_MAP = {
    "rapidly-growing": "rapidly-growing",
    "growing": "growing",
    "stable": "stable",
    "declining": "declining",
}


async def get_skill_demand(
    db: AsyncIOMotorDatabase,
    industry: str | None = None,
    district: str | None = None,
) -> list[dict]:
    """Return skill demand records from the skill_demand collection."""
    q: dict = {}
    if industry:
        q["category"] = {"$regex": industry, "$options": "i"}
    if district and district != "Maharashtra":
        q["location"] = {"$regex": district, "$options": "i"}

    cursor = db.skill_demand.find(q).sort("current_demand", -1).limit(100)
    docs = await cursor.to_list(length=100)

    result = []
    for d in docs:
        result.append({
            "skill": d.get("skill_name", d.get("skill", "")),
            "category": d.get("category", ""),
            "currentDemand": d.get("current_demand", 0),
            "growthRate": d.get("growth_rate", 0),
            "jobCount": d.get("job_count", 0),
            "supply": d.get("supply", 0),
            "status": d.get("status", "stable"),
            "region": d.get("location", "Maharashtra"),
        })
    return result


async def get_skill_demand_detail(skill_id: str, db: AsyncIOMotorDatabase) -> dict | None:
    doc = await db.skill_demand.find_one({"skill_id": skill_id})
    if not doc:
        return None
    return {
        "skill": doc.get("skill_name", ""),
        "skill_id": skill_id,
        "current_demand": doc.get("current_demand", 0),
        "growth_rate": doc.get("growth_rate", 0),
        "job_count": doc.get("job_count", 0),
        "supply": doc.get("supply", 0),
        "status": doc.get("status", "stable"),
        "industry_demand": doc.get("industry_demand", {}),
        "regional_demand": doc.get("regional_demand", {}),
        "classification": _classify(doc.get("growth_rate", 0)),
    }


def _classify(growth_rate: int) -> str:
    if growth_rate >= 30: return "RAPIDLY_GROWING"
    if growth_rate >= 10: return "GROWING"
    if growth_rate >= 0: return "STABLE"
    return "DECLINING"
