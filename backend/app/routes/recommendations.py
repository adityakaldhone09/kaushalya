from __future__ import annotations
import logging
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.connection import get_db
from app.services.skill_gap import analyze_skill_gap, ROLE_SKILL_MAP

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Trainees"])


@router.get("/recommendations/{trainee_id}")
async def get_recommendations(
    trainee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    profile = await db.trainee_profiles.find_one({"user_id": trainee_id})
    if not profile:
        # Fallback to first trainee (demo)
        profile = await db.trainee_profiles.find_one({})
        if profile:
            trainee_id = profile.get("user_id", trainee_id)

    target_role = (profile or {}).get("target_career", "Cloud Engineer")
    gap = await analyze_skill_gap(trainee_id, target_role, db)

    recs = []

    # Skill gap recommendations
    for skill in gap.get("priority_skills", [])[:2]:
        recs.append({
            "id": f"rec-skill-{skill.lower().replace(' ', '-')}",
            "type": "skill",
            "title": f"Close your {skill} gap",
            "description": f"{skill} is a high-impact skill for {target_role} roles. Build it now to unlock more matches.",
            "action": f"Start {skill} fundamentals",
            "priority": "high",
        })

    # Training recommendations
    training_programs = gap.get("recommended_training", [])
    for prog_name in training_programs[:1]:
        prog = await db.training_programs.find_one(
            {"name": {"$regex": prog_name[:15], "$options": "i"}}
        )
        if prog:
            recs.append({
                "id": f"rec-training-{str(prog['_id'])}",
                "type": "training",
                "title": prog.get("name", prog_name),
                "description": f"A {prog.get('duration', '')} {prog.get('mode', '')} program with {prog.get('placement_rate', 0)}% placement rate.",
                "action": "View program",
                "priority": "high",
            })

    # Job recommendations
    job = await db.jobs.find_one({"status": "open"})
    if job:
        recs.append({
            "id": f"rec-job-{str(job['_id'])}",
            "type": "job",
            "title": f"{job.get('title', 'Job')} at {job.get('company', '')}",
            "description": f"Your profile is a strong match based on your current skills.",
            "action": "Review job",
            "priority": "medium",
        })

    return recs or [
        {
            "id": "rec-default-001",
            "type": "skill",
            "title": "Complete your profile",
            "description": "A complete profile improves your match quality for jobs and training programs.",
            "action": "Update profile",
            "priority": "high",
        }
    ]
