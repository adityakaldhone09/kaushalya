from __future__ import annotations
from motor.motor_asyncio import AsyncIOMotorDatabase
from .gemini_client import generate_text, is_available
from .prompts import KAUSHALYA_SYSTEM, DISTRICT_INSIGHT


async def get_district_insight(district_name: str, db: AsyncIOMotorDatabase) -> dict:
    doc = await db.district_data.find_one(
        {"district": {"$regex": f"^{district_name}$", "$options": "i"}}
    ) or {}

    demand_cursor = db.skill_demand.find(
        {"location": {"$regex": district_name, "$options": "i"}}
    ).sort("current_demand", -1).limit(5)
    demand_docs = await demand_cursor.to_list(length=5)

    training_cursor = db.training_programs.find(
        {"location": {"$regex": district_name, "$options": "i"}}
    ).limit(4)
    training_docs = await training_cursor.to_list(length=4)

    workforce = (
        f"Trainees: {doc.get('trainees', 'N/A')}\n"
        f"Employed: {doc.get('employed', 'N/A')}\n"
        f"Placement Rate: {doc.get('placement_rate', 'N/A')}%\n"
        f"Average Salary: {doc.get('average_salary', 'N/A')}\n"
        f"Skill Gap: {doc.get('skill_gap', 'N/A')}\n"
        f"Top Demand Skill: {doc.get('top_demand', 'N/A')}"
    )
    demand_text = "\n".join(
        f"- {d.get('skill_name','')}: demand={d.get('current_demand',0)} growth=+{d.get('growth_rate',0)}%"
        for d in demand_docs
    ) or "No demand data."
    training_text = "\n".join(
        f"- {p.get('name','')}: {p.get('placement_rate',0)}% placement"
        for p in training_docs
    ) or "No programs."

    if is_available():
        prompt = DISTRICT_INSIGHT.format(
            system=KAUSHALYA_SYSTEM,
            district=district_name,
            workforce_data=workforce,
            skill_demand=demand_text,
            training_data=training_text,
        )
        answer, is_ai = await generate_text(prompt, max_output_tokens=800)
        if answer:
            return {"insight": answer, "district_data": doc, "is_ai_generated": is_ai}

    # Deterministic fallback
    recommendation = doc.get("recommendation", "Review training capacity and employer partnerships.")
    insight = (
        f"{district_name} District Intelligence:\n"
        f"• Placement Rate: {doc.get('placement_rate','N/A')}%\n"
        f"• Top Demand: {doc.get('top_demand','N/A')}\n"
        f"• Skill Gap Status: {doc.get('skill_gap','N/A')}\n"
        f"• Recommendation: {recommendation}\n"
        "[AI unavailable — showing database statistics]"
    )
    return {"insight": insight, "district_data": doc, "is_ai_generated": False}
