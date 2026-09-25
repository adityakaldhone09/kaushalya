from __future__ import annotations
"""
Training Program Impact Calculator.

Impact weights:
  Placement Rate        30%
  Retention             20%
  Salary Improvement    15%
  Skill Relevance       20%
  Employer Satisfaction 15%
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


async def get_program_impact(program_id: str, db: AsyncIOMotorDatabase) -> dict | None:
    program = None
    if ObjectId.is_valid(program_id):
        program = await db.training_programs.find_one({"_id": ObjectId(program_id)})
    if not program:
        return None

    # Existing metrics from the program document
    placement_rate = program.get("placement_rate", 0)
    completion_rate = program.get("completion_rate", 0)

    # Retention from employment outcomes
    pipeline = [
        {"$match": {"training_program_id": program_id}},
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "retained_6m": {"$sum": {"$cond": ["$retention_6_months", 1, 0]}},
            "avg_salary": {"$avg": "$salary"},
        }},
    ]
    agg = await db.employment_outcomes.aggregate(pipeline).to_list(length=1)
    agg_data = agg[0] if agg else {}
    total_outcomes = agg_data.get("total", 0)
    retention_rate = (
        int(agg_data["retained_6m"] / total_outcomes * 100) if total_outcomes else 65
    )
    avg_salary = agg_data.get("avg_salary", 4.5) or 4.5

    # Weighted score
    placement_pts = int(placement_rate / 100 * 30)
    retention_pts = int(retention_rate / 100 * 20)
    salary_pts = min(15, int((avg_salary / 10) * 15))  # normalise to 10 LPA max
    skill_relevance_pts = _skill_relevance_pts(program)
    employer_sat_pts = 10  # default placeholder

    impact_score = placement_pts + retention_pts + salary_pts + skill_relevance_pts + employer_sat_pts
    impact_score = min(100, max(0, impact_score))

    return {
        "program_id": program_id,
        "program_name": program.get("name", ""),
        "impact_score": impact_score,
        "classification": _classify(impact_score),
        "metrics": {
            "placement_rate": placement_rate,
            "completion_rate": completion_rate,
            "retention_rate": retention_rate,
            "average_salary": round(avg_salary, 2),
            "total_outcomes": total_outcomes,
        },
        "strengths": _strengths(placement_rate, retention_rate, skill_relevance_pts),
        "weaknesses": _weaknesses(placement_rate, retention_rate),
        "recommendations": _recommendations(program, placement_rate, retention_rate),
    }


async def list_program_impacts(db: AsyncIOMotorDatabase) -> list[dict]:
    cursor = db.training_programs.find().limit(20)
    programs = await cursor.to_list(length=20)
    results = []
    for p in programs:
        impact = await get_program_impact(str(p["_id"]), db)
        if impact:
            results.append(impact)
    results.sort(key=lambda x: x["impact_score"], reverse=True)
    return results


def _skill_relevance_pts(program: dict) -> int:
    skills = program.get("skills", [])
    high_demand = {"AWS", "Docker", "Cybersecurity", "Data Science", "Python", "Solar Energy"}
    matched = sum(1 for s in skills if s in high_demand)
    return min(20, 8 + matched * 4)


def _classify(score: int) -> str:
    if score >= 80: return "EXCELLENT"
    if score >= 65: return "GOOD"
    if score >= 50: return "AVERAGE"
    return "NEEDS_IMPROVEMENT"


def _strengths(placement: int, retention: int, skill_pts: int) -> list[str]:
    s = []
    if placement >= 70: s.append("High placement rate demonstrates strong industry connections")
    if retention >= 70: s.append("Strong 6-month retention indicates good job-fit matching")
    if skill_pts >= 16: s.append("Curriculum closely aligned with high-demand skills")
    if not s: s.append("Program is building foundational employability")
    return s


def _weaknesses(placement: int, retention: int) -> list[str]:
    w = []
    if placement < 60: w.append("Placement rate below regional average — strengthen employer partnerships")
    if retention < 60: w.append("Retention needs improvement — add post-placement mentorship")
    if not w: w.append("Continue monitoring to sustain current performance")
    return w


def _recommendations(program: dict, placement: int, retention: int) -> list[str]:
    r = []
    if placement < 65:
        r.append(f"Expand employer outreach for {program.get('industry', 'industry')} roles")
    if retention < 65:
        r.append("Introduce 3-month post-placement check-in program")
    r.append(f"Consider adding capstone project assessment to {program.get('name', 'this program')}")
    return r
