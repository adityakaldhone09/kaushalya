from __future__ import annotations
"""
Employability Score Calculator
Weights: Skills 30 | Assessment 15 | Training 15 | Certs 10 | Experience 10 | Demand 10 | Profile 10
"""
from motor.motor_asyncio import AsyncIOMotorDatabase


async def calculate_employability(user_id: str, db: AsyncIOMotorDatabase) -> dict:
    profile = await db.trainee_profiles.find_one({"user_id": user_id})
    if not profile:
        return _empty_score()

    # Fast path — use cached value when present (seeded or previously computed)
    cached = profile.get("cached_employability_score")
    if cached is not None:
        cls = profile.get("cached_score_class", _classify(cached))
        return {
            "score": cached,
            "classification": cls,
            "breakdown": {
                "skills":        int(cached * 0.30),
                "assessment":    int(cached * 0.15),
                "training":      int(cached * 0.15),
                "certifications":int(cached * 0.10),
                "experience":    int(cached * 0.10),
                "demand":        int(cached * 0.10),
                "profile":       int(cached * 0.10),
            },
        }

    # 1. Skills Match (30 pts)
    user_skills = await db.user_skills.find({"user_id": user_id}).to_list(length=100)
    skills_score = 0
    if user_skills:
        avg_prof       = sum(s.get("proficiency", 0) for s in user_skills) / len(user_skills)
        verified_ratio = sum(1 for s in user_skills if s.get("verified")) / len(user_skills)
        threshold_ratio= sum(1 for s in user_skills if s.get("proficiency", 0) >= 60) / len(user_skills)
        skills_score   = int((avg_prof / 100 * 0.5 + verified_ratio * 0.3 + threshold_ratio * 0.2) * 30)

    # 2. Assessment Performance (15 pts)
    results = await db.assessment_results.find({"user_id": user_id}).to_list(length=50)
    assessment_score = 0
    if results:
        avg_pct = sum(r.get("percentage", 0) for r in results) / len(results)
        assessment_score = int(avg_pct / 100 * 15)

    # 3. Training Completion (15 pts)
    completed_count   = await db.enrollments.count_documents({"trainee_id": user_id, "status": "COMPLETED"})
    all_enrolled_count= await db.enrollments.count_documents({"trainee_id": user_id})
    training_score = 0
    if all_enrolled_count:
        training_score = int(completed_count / all_enrolled_count * 15)
    elif completed_count:
        training_score = 10

    # 4. Certifications (10 pts)
    cert_count  = await db.certifications.count_documents({"user_id": user_id})
    cert_score  = min(10, cert_count * 5)

    # 5. Experience (10 pts)
    exp = profile.get("experience", "").lower()
    if any(x in exp for x in ("3", "4", "5", "senior")):
        exp_score = 10
    elif any(x in exp for x in ("2", "year")):
        exp_score = 7
    elif any(x in exp for x in ("1", "fresher", "intern")):
        exp_score = 4
    elif exp:
        exp_score = 2
    else:
        exp_score = 0

    # 6. Industry Demand (10 pts)
    demand_score = 6
    if user_skills:
        high_demand = {"aws", "cloud computing", "cybersecurity", "data science", "docker", "python", "kubernetes"}
        matched = sum(1 for s in user_skills if s.get("skill_name", "").lower() in high_demand)
        demand_score = min(10, 4 + matched * 2)

    # 7. Profile Completion (10 pts)
    profile_score = int(_calc_profile_completion(profile) / 100 * 10)

    total = min(100, max(0,
        skills_score + assessment_score + training_score +
        cert_score + exp_score + demand_score + profile_score
    ))

    # Cache result back to profile so next call is instant
    await db.trainee_profiles.update_one(
        {"user_id": user_id},
        {"$set": {"cached_employability_score": total, "cached_score_class": _classify(total)}},
    )

    return {
        "score": total,
        "classification": _classify(total),
        "breakdown": {
            "skills":         skills_score,
            "assessment":     assessment_score,
            "training":       training_score,
            "certifications": cert_score,
            "experience":     exp_score,
            "demand":         demand_score,
            "profile":        profile_score,
        },
    }


def _classify(score: int) -> str:
    if score >= 80: return "HIGH"
    if score >= 60: return "MEDIUM"
    return "LOW"


def _calc_profile_completion(profile: dict) -> int:
    fields = ["name", "email", "phone", "district", "education", "specialization",
              "employment_status", "experience", "target_career"]
    filled = sum(1 for f in fields if profile.get(f))
    return int(filled / len(fields) * 100)


def _empty_score() -> dict:
    return {
        "score": 0,
        "classification": "LOW",
        "breakdown": {k: 0 for k in
                      ("skills", "assessment", "training", "certifications",
                       "experience", "demand", "profile")},
    }
