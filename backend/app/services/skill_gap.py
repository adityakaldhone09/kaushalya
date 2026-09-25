from __future__ import annotations
"""
Skill Gap Engine — pure Python deterministic calculation, no LLM.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase

# Role → required skills with minimum proficiency thresholds
ROLE_SKILL_MAP: dict[str, dict[str, int]] = {
    "Cloud Engineer": {"AWS": 70, "Docker": 65, "Linux": 60, "Python": 60, "Kubernetes": 50},
    "DevOps Engineer": {"AWS": 65, "Docker": 70, "CI/CD": 65, "Python": 60, "Linux": 65},
    "Backend Developer": {"Python": 70, "SQL": 65, "REST APIs": 60, "Git": 50},
    "Data Scientist": {"Python": 75, "SQL": 65, "Data Science": 70, "Machine Learning": 60},
    "Full Stack Developer": {"React": 65, "Python": 60, "SQL": 55, "REST APIs": 60},
    "Cybersecurity Analyst": {"Cybersecurity": 70, "Networking": 60, "Linux": 55},
    "Data Operations Analyst": {"SQL": 65, "Excel": 55, "Communication": 60},
    "Solar Technician": {"Solar Energy": 65, "Electrical Safety": 60},
    "Logistics Tech Analyst": {"Logistics Tech": 65, "SQL": 55, "Communication": 60},
    "Agritech Specialist": {"Agritech": 65, "IoT": 55, "Communication": 60},
}

_TRAINING_MAP: dict[str, str] = {
    "AWS": "Cloud & DevOps Accelerator",
    "Docker": "Cloud & DevOps Accelerator",
    "Kubernetes": "Cloud & DevOps Accelerator",
    "Python": "Applied Data Science",
    "Data Science": "Applied Data Science",
    "Machine Learning": "Applied Data Science",
    "SQL": "Applied Data Science",
    "Solar Energy": "Solar Technician Pathway",
    "React": "Full Stack Web Development",
    "Cybersecurity": "Cybersecurity Operations",
}


async def analyze_skill_gap(
    user_id: str,
    target_role: str,
    db: AsyncIOMotorDatabase,
    target_skills: list[str] | None = None,
) -> dict:
    # Get user's current skills
    skills_cursor = db.user_skills.find({"user_id": user_id})
    user_skills_docs = await skills_cursor.to_list(length=100)
    user_skill_map: dict[str, int] = {
        s.get("skill_name", ""): s.get("proficiency", 0)
        for s in user_skills_docs
    }

    # Determine required skills
    if target_skills:
        required = {s: 60 for s in target_skills}
    else:
        required = ROLE_SKILL_MAP.get(target_role, {})
        if not required:
            # Generic fallback — use top demand skills
            required = {"Python": 60, "SQL": 55, "Communication": 55}

    matching_skills: list[str] = []
    weak_skills: list[dict] = []
    missing_skills: list[str] = []
    priority_skills: list[str] = []

    for skill, threshold in required.items():
        current = user_skill_map.get(skill, 0)
        gap = max(0, threshold - current)

        if current >= threshold:
            matching_skills.append(skill)
        elif current > 0:
            weak_skills.append({
                "skill": skill,
                "category": _guess_category(skill),
                "required_proficiency": threshold,
                "current_proficiency": current,
                "gap": gap,
                "priority": "high" if gap > 30 else "medium",
                "status": "weak",
            })
            if gap > 20:
                priority_skills.append(skill)
        else:
            missing_skills.append(skill)
            priority_skills.append(skill)

    total_required = len(required)
    match_pct = int(len(matching_skills) / total_required * 100) if total_required else 0

    # Recommended training programs
    recommended: list[str] = []
    for skill in priority_skills[:3]:
        prog = _TRAINING_MAP.get(skill)
        if prog and prog not in recommended:
            recommended.append(prog)

    return {
        "overall_match": match_pct,
        "target_role": target_role,
        "matching_skills": matching_skills,
        "weak_skills": weak_skills,
        "missing_skills": missing_skills,
        "priority_skills": priority_skills[:5],
        "recommended_training": recommended,
    }


def _guess_category(skill: str) -> str:
    mapping = {
        "AWS": "Cloud Computing", "Docker": "Cloud Computing", "Kubernetes": "Cloud Computing",
        "Python": "Software Development", "React": "Software Development", "Git": "Software Development",
        "SQL": "Data Science", "Data Science": "Data Science", "Machine Learning": "Data Science",
        "Cybersecurity": "Cybersecurity",
        "Solar Energy": "Green Energy",
        "Communication": "Soft Skills",
    }
    return mapping.get(skill, "Technical")
