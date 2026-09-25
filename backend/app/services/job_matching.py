from __future__ import annotations
"""
Job Matching Engine — deterministic scoring, no LLM.

Match weights:
  Skill Match      40%
  Experience       20%
  Education        10%
  Location         10%
  Semantic/Role    20%
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.utils.serializer import serialize_doc


async def get_job_matches(user_id: str, db: AsyncIOMotorDatabase) -> list[dict]:
    profile = await db.trainee_profiles.find_one({"user_id": user_id})
    skills_cursor = db.user_skills.find({"user_id": user_id})
    user_skills = await skills_cursor.to_list(length=100)

    skill_map: dict[str, int] = {s.get("skill_name", ""): s.get("proficiency", 0) for s in user_skills}
    user_district = (profile or {}).get("district", "").lower()
    user_experience = (profile or {}).get("experience", "").lower()
    target_career = (profile or {}).get("target_career", "").lower()

    # Get open jobs
    jobs_cursor = db.jobs.find({"status": "open"}).limit(50)
    jobs = await jobs_cursor.to_list(length=50)

    matches = []
    for job in jobs:
        score, matching, missing = _score_job(
            job, skill_map, user_district, user_experience, target_career
        )
        doc = serialize_doc(job) or {}
        # Normalise field names to match the existing OpenAPI contract
        matches.append({
            "id": doc.get("id") or doc.get("_id", ""),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "industry": job.get("industry", ""),
            "location": job.get("location", ""),
            "job_type": job.get("job_type", job.get("jobType", "Full-time")),
            "experience": job.get("experience", ""),
            "salary": job.get("salary", ""),
            "required_skills": job.get("required_skills", job.get("requiredSkills", [])),
            "posted": job.get("posted", ""),
            "deadline": job.get("deadline", ""),
            "applicants": job.get("applicants", 0),
            "match": score,
            "matching_skills": matching,
            "missing_skills": missing,
            "match_reason": f"{len(matching)} of {len(job.get('required_skills', job.get('requiredSkills', [])))} priority skills match your profile.",
        })

    matches.sort(key=lambda x: x["match"], reverse=True)
    return matches


def _score_job(
    job: dict,
    skill_map: dict[str, int],
    user_district: str,
    user_experience: str,
    target_career: str,
) -> tuple[int, list[str], list[str]]:
    required = job.get("required_skills", job.get("requiredSkills", []))

    # 1. Skill match (40 pts)
    matching = [s for s in required if skill_map.get(s, 0) >= 60]
    missing = [s for s in required if s not in matching]
    skill_ratio = len(matching) / len(required) if required else 0
    skill_pts = int(skill_ratio * 40)

    # 2. Experience match (20 pts)
    job_exp = job.get("experience", "").lower()
    exp_pts = 0
    if "0" in job_exp or "fresher" in job_exp or "entry" in job_exp:
        exp_pts = 20 if not user_experience or "fresher" in user_experience or "0" in user_experience else 14
    elif "1" in job_exp or "junior" in job_exp:
        exp_pts = 18 if "1" in user_experience else 10
    elif "2" in job_exp or "mid" in job_exp:
        exp_pts = 16 if any(x in user_experience for x in ["2", "3"]) else 8
    else:
        exp_pts = 12

    # 3. Education (10 pts) — always award base
    edu_pts = 7

    # 4. Location match (10 pts)
    job_location = job.get("location", "").lower()
    loc_pts = 0
    if user_district and user_district in job_location:
        loc_pts = 10
    elif "remote" in job_location:
        loc_pts = 9
    elif "hybrid" in job_location:
        loc_pts = 7
    else:
        loc_pts = 4

    # 5. Semantic / role match (20 pts)
    role_pts = 0
    job_title = job.get("title", "").lower()
    if target_career and any(word in job_title for word in target_career.split()):
        role_pts = 20
    elif any(skill.lower() in job_title for skill in skill_map if skill_map[skill] >= 60):
        role_pts = 14
    else:
        role_pts = 8

    total = skill_pts + exp_pts + edu_pts + loc_pts + role_pts
    return min(100, max(0, total)), matching, missing
