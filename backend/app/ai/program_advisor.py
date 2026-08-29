from __future__ import annotations
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from .gemini_client import generate_text, is_available
from .prompts import KAUSHALYA_SYSTEM, PROGRAM_INSIGHT


async def get_program_insight(program_id: str, db: AsyncIOMotorDatabase) -> dict:
    program = None
    if ObjectId.is_valid(program_id):
        program = await db.training_programs.find_one({"_id": ObjectId(program_id)})
    if not program:
        program = await db.training_programs.find_one({}) or {}

    name = program.get("name", "This Program")
    institute = program.get("institute", "")
    placement = program.get("placement_rate", 0)
    completion = program.get("completion_rate", 0)
    impact = program.get("impact_score", 0)
    salary = program.get("salary", "N/A")

    # Retention from outcomes
    pid = str(program.get("_id", ""))
    pipeline = [
        {"$match": {"training_program_id": pid}},
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "retained": {"$sum": {"$cond": ["$retention_6_months", 1, 0]}},
        }},
    ]
    agg = await db.employment_outcomes.aggregate(pipeline).to_list(length=1)
    agg_data = agg[0] if agg else {}
    retention = round(
        agg_data.get("retained", 0) / agg_data.get("total", 1) * 100, 1
    ) if agg_data.get("total") else 65

    if is_available():
        prompt = PROGRAM_INSIGHT.format(
            system=KAUSHALYA_SYSTEM,
            program_name=name,
            institute=institute,
            placement_rate=placement,
            completion_rate=completion,
            impact_score=impact,
            avg_salary=salary,
            retention_rate=retention,
        )
        answer, is_ai = await generate_text(prompt, max_output_tokens=700)
        if answer:
            return {"insight": answer, "metrics": {
                "placement_rate": placement, "completion_rate": completion,
                "impact_score": impact, "retention_rate": retention,
            }, "is_ai_generated": is_ai}

    insight = (
        f"{name} — Program Performance:\n"
        f"• Placement Rate: {placement}%\n"
        f"• Completion Rate: {completion}%\n"
        f"• Impact Score: {impact}/100\n"
        f"• 6-Month Retention: {retention}%\n"
        f"• Average Salary: {salary}\n"
        "[AI unavailable — showing calculated metrics]"
    )
    return {"insight": insight, "metrics": {
        "placement_rate": placement, "completion_rate": completion,
        "impact_score": impact, "retention_rate": retention,
    }, "is_ai_generated": False}
