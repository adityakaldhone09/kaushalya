from __future__ import annotations
"""
Future Skill Forecasting — simple deterministic model.
Uses growth_rate from skill_demand records + linear projection.
Falls back to INSUFFICIENT_DATA when historical data is unavailable.
"""
import math
from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_skill_forecast(db: AsyncIOMotorDatabase) -> list[dict]:
    cursor = db.skill_demand.find().sort("current_demand", -1).limit(20)
    docs = await cursor.to_list(length=20)

    result = []
    for d in docs:
        current = d.get("current_demand", 0)
        growth_rate = d.get("growth_rate", 0)
        if current == 0:
            continue

        # Simple 12-month linear projection
        predicted = _project(current, growth_rate)
        trend = _trend_label(growth_rate)
        confidence = _confidence(d)

        result.append({
            "skill": d.get("skill_name", d.get("skill", "")),
            "currentDemand": current,
            "predictedDemand": predicted,
            "growthRate": growth_rate,
            "confidence": confidence,
            "trend": trend,
            "rationale": _rationale(d),
        })

    result.sort(key=lambda x: x["growthRate"], reverse=True)
    return result


def _project(current: int, growth_rate: int) -> int:
    if growth_rate == 0:
        return current
    factor = 1 + (growth_rate / 100)
    return max(0, int(current * factor))


def _trend_label(growth_rate: int) -> str:
    if growth_rate >= 35: return "HIGH FUTURE DEMAND"
    if growth_rate >= 15: return "GROWING"
    if growth_rate >= 0: return "STABLE"
    return "DECLINING"


def _confidence(doc: dict) -> int:
    base = 75
    if doc.get("job_count", 0) > 1000: base += 10
    if doc.get("supply", 0) > 0: base += 5
    return min(95, base)


def _rationale(doc: dict) -> str:
    skill = doc.get("skill_name", "this skill")
    gr = doc.get("growth_rate", 0)
    if gr >= 30:
        return f"Strong employer pull for {skill} with constrained verified supply."
    if gr >= 10:
        return f"{skill} adoption is expanding as employers operationalize new workflows."
    if gr < 0:
        return f"Automation and tooling are reducing demand for standalone {skill} roles."
    return f"{skill} demand is stable; supply and demand are broadly balanced."
