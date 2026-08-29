from __future__ import annotations
"""
Context Builder — retrieves only the data needed to answer a question.
Never sends raw MongoDB documents or secrets to Gemini.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

logger = logging.getLogger(__name__)


async def build_trainee_context(user_id: str, db: AsyncIOMotorDatabase) -> dict:
    """Build compact, sanitised context for a trainee user."""
    profile = await db.trainee_profiles.find_one({"user_id": user_id}) or {}
    skills_cursor = db.user_skills.find({"user_id": user_id})
    skills_docs = await skills_cursor.to_list(length=30)

    skills = [
        {
            "name": s.get("skill_name", ""),
            "category": s.get("category", ""),
            "proficiency": s.get("proficiency", 0),
            "verified": s.get("verified", False),
        }
        for s in skills_docs
    ]

    # Assessment results — last 5
    results_cursor = db.assessment_results.find({"user_id": user_id}).sort("completed_at", -1)
    results = await results_cursor.to_list(length=5)
    assessments = [
        {
            "skill": r.get("skill_name", ""),
            "score": r.get("percentage", 0),
            "level": r.get("proficiency_level", ""),
        }
        for r in results
    ]

    # Certifications
    certs_cursor = db.certifications.find({"user_id": user_id})
    certs = await certs_cursor.to_list(length=10)
    certifications = [c.get("name", "") for c in certs]

    # Active enrollments
    enroll_cursor = db.enrollments.find({"trainee_id": user_id, "status": {"$in": ["IN_PROGRESS", "ENROLLED"]}})
    enrollments = await enroll_cursor.to_list(length=5)
    active_programs = [e.get("program_name", "") for e in enrollments]

    # Employment outcomes
    outcome = await db.employment_outcomes.find_one(
        {"trainee_id": user_id}, sort=[("employment_date", -1)]
    )

    # Cached employability score
    emp_score = profile.get("cached_employability_score", 0)
    score_class = profile.get("cached_score_class", "LOW")

    return {
        "name": profile.get("name", ""),
        "education": f"{profile.get('education', '')} {profile.get('specialization', '')}".strip(),
        "district": profile.get("district", ""),
        "state": profile.get("state", "Maharashtra"),
        "experience": profile.get("experience", ""),
        "employment_status": profile.get("employment_status", ""),
        "target_career": profile.get("target_career", ""),
        "profile_completion": profile.get("profile_completion", 0),
        "employability_score": emp_score,
        "score_class": score_class,
        "skills": skills,
        "assessments": assessments,
        "certifications": certifications,
        "active_programs": active_programs,
        "current_employer": profile.get("company"),
        "current_role": profile.get("job_role"),
        "current_salary": profile.get("salary"),
        "employment_outcome": {
            "employer": outcome.get("employer_name", "") if outcome else "",
            "role": outcome.get("job_title", "") if outcome else "",
        } if outcome else None,
    }


async def build_employer_context(user_id: str, db: AsyncIOMotorDatabase) -> dict:
    employer = await db.employers.find_one({"user_id": user_id}) or {}
    jobs_cursor = db.jobs.find({"employer_id": user_id, "status": "open"}).limit(10)
    jobs = await jobs_cursor.to_list(length=10)
    return {
        "company": employer.get("company_name", ""),
        "industry": employer.get("industry", ""),
        "location": employer.get("location", ""),
        "open_jobs": [{"title": j.get("title", ""), "skills": j.get("required_skills", [])} for j in jobs],
        "total_open_jobs": len(jobs),
    }


async def build_institute_context(user_id: str, db: AsyncIOMotorDatabase) -> dict:
    programs_cursor = db.training_programs.find({"created_by": user_id}).limit(10)
    programs = await programs_cursor.to_list(length=10)
    return {
        "programs": [
            {
                "name": p.get("name", ""),
                "placement_rate": p.get("placement_rate", 0),
                "completion_rate": p.get("completion_rate", 0),
                "enrolled": p.get("enrolled", 0),
                "skills": p.get("skills", []),
            }
            for p in programs
        ],
        "total_programs": len(programs),
    }


async def build_government_context(db: AsyncIOMotorDatabase) -> dict:
    """Aggregate-level context for government admins — no individual PII."""
    total_trainees = await db.trainee_profiles.count_documents({})
    employed = await db.trainee_profiles.count_documents({"employment_status": "Employed"})
    total_programs = await db.training_programs.count_documents({})
    total_jobs = await db.jobs.count_documents({"status": "open"})

    # Top skill demand
    top_demand_cursor = db.skill_demand.find().sort("current_demand", -1).limit(5)
    top_demand = await top_demand_cursor.to_list(length=5)

    # District summaries
    districts_cursor = db.district_data.find().sort("placement_rate", -1).limit(5)
    districts = await districts_cursor.to_list(length=5)

    return {
        "total_trainees": total_trainees,
        "employed_trainees": employed,
        "employment_rate": round(employed / total_trainees * 100, 1) if total_trainees else 0,
        "total_programs": total_programs,
        "open_jobs": total_jobs,
        "top_demanded_skills": [
            {"skill": d.get("skill_name", ""), "demand": d.get("current_demand", 0), "growth": d.get("growth_rate", 0)}
            for d in top_demand
        ],
        "top_districts": [
            {"district": d.get("district", ""), "placement_rate": d.get("placement_rate", 0), "status": d.get("status", "")}
            for d in districts
        ],
    }


def format_profile_for_prompt(ctx: dict) -> str:
    """Convert trainee context dict to readable text for the prompt."""
    lines = [
        f"Name: {ctx.get('name', 'Unknown')}",
        f"Education: {ctx.get('education', 'Not specified')}",
        f"District: {ctx.get('district', '')} | Experience: {ctx.get('experience', '')}",
        f"Target Career: {ctx.get('target_career', 'Not set')}",
        f"Employment Status: {ctx.get('employment_status', '')}",
        f"Employability Score: {ctx.get('employability_score', 0)}/100 ({ctx.get('score_class', '')})",
        "",
        "Skills:",
    ]
    for s in ctx.get("skills", [])[:10]:
        verified = "✓" if s.get("verified") else "○"
        lines.append(f"  {verified} {s['name']}: {s['proficiency']}% ({s.get('category', '')})")

    if ctx.get("certifications"):
        lines.append(f"\nCertifications: {', '.join(ctx['certifications'][:5])}")
    if ctx.get("active_programs"):
        lines.append(f"Active Training: {', '.join(ctx['active_programs'][:3])}")

    return "\n".join(lines)


def format_skill_gaps_for_prompt(gap_data: dict) -> str:
    lines = [
        f"Target Role: {gap_data.get('target_role', '')}",
        f"Overall Match: {gap_data.get('overall_match', 0)}%",
        f"Missing Skills: {', '.join(gap_data.get('missing_skills', []))}",
        f"Priority Skills: {', '.join(gap_data.get('priority_skills', [])[:5])}",
    ]
    for w in gap_data.get("weak_skills", [])[:5]:
        lines.append(f"  Weak: {w.get('skill', '')} — current {w.get('current_proficiency', 0)}%, need {w.get('required_proficiency', 0)}%")
    return "\n".join(lines)
