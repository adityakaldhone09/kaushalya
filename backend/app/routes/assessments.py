from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.utils.serializer import serialize_doc, serialize_docs
from app.models.base import utcnow

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assessments", tags=["Assessments"])


def _proficiency_level(pct: int) -> str:
    """Map percentage to proficiency level."""
    if pct >= 86:
        return "Expert"
    if pct >= 71:
        return "Advanced"
    if pct >= 51:
        return "Intermediate"
    if pct >= 31:
        return "Basic"
    return "Beginner"


class AssessmentStartResponse(BaseModel):
    """Response when starting an assessment attempt."""
    attempt_id: str
    assessment_id: str
    time_limit_minutes: int
    question_count: int
    started_at: str


# ────────────────────────────────────────────────────────────────────────────
# LIST ASSESSMENTS
# ────────────────────────────────────────────────────────────────────────────

@router.get("")
async def list_assessments(db: AsyncIOMotorDatabase = Depends(get_db)):
    """List available assessments (without questions/answers)."""
    cursor = db.skill_assessments.find({"active": True}).limit(50)
    docs = await cursor.to_list(length=50)
    result = []
    for d in docs:
        r = serialize_doc(d) or {}
        r.pop("questions", None)
        result.append(r)
    return result


@router.get("/history/me")
async def my_assessment_history(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get all assessment attempts for the current user."""
    user_id = str(user["_id"])
    cursor = db.assessment_attempts.find({"user_id": user_id}).sort("started_at", -1)
    docs = await cursor.to_list(length=100)
    return serialize_docs(docs)


@router.get("/results/me")
async def my_results(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get all assessment results for the current user."""
    user_id = str(user["_id"])
    cursor = db.assessment_results.find({"user_id": user_id}).sort("completed_at", -1)
    docs = await cursor.to_list(length=100)
    return serialize_docs(docs)


@router.get("/{assessment_id}")
async def get_assessment(
    assessment_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get a specific assessment."""
    try:
        doc = await db.skill_assessments.find_one({"_id": ObjectId(assessment_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid assessment ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    result = serialize_doc(doc) or {}
    # Strip correct_option_id from questions before sending to client
    for q in result.get("questions", []):
        q.pop("correct_option_id", None)
    return result


# ────────────────────────────────────────────────────────────────────────────
# START ASSESSMENT ATTEMPT
# ────────────────────────────────────────────────────────────────────────────

@router.post("/{assessment_id}/start", response_model=AssessmentStartResponse)
async def start_assessment(
    assessment_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Start a new assessment attempt."""
    user_id = str(user["_id"])
    
    try:
        assessment = await db.skill_assessments.find_one({"_id": ObjectId(assessment_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid assessment ID")
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if not assessment.get("active", True):
        raise HTTPException(status_code=403, detail="Assessment is not active")
    
    questions = assessment.get("questions", [])
    if not questions:
        raise HTTPException(status_code=400, detail="Assessment has no questions")
    
    now = utcnow()
    duration_minutes = assessment.get("duration_minutes", 30)
    
    # Create attempt record
    attempt_doc = {
        "user_id": user_id,
        "assessment_id": assessment_id,
        "skill_id": assessment.get("skill_id", ""),
        "skill_name": assessment.get("skill_name", ""),
        "started_at": now,
        "time_limit_minutes": duration_minutes,
        "expires_at": now + timedelta(minutes=duration_minutes),
        "status": "in_progress",
        "answers": {},
        "submitted_at": None,
        "completed_at": None,
    }
    
    result = await db.assessment_attempts.insert_one(attempt_doc)
    attempt_doc["_id"] = result.inserted_id
    
    logger.info(f"Assessment attempt started: {result.inserted_id} for user {user_id}")
    
    return AssessmentStartResponse(
        attempt_id=str(result.inserted_id),
        assessment_id=assessment_id,
        time_limit_minutes=duration_minutes,
        question_count=len(questions),
        started_at=now.isoformat(),
    )


# ────────────────────────────────────────────────────────────────────────────
# GET ATTEMPT STATUS
# ────────────────────────────────────────────────────────────────────────────

@router.get("/attempts/{attempt_id}")
async def get_attempt(
    attempt_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get current assessment attempt status and questions."""
    user_id = str(user["_id"])
    
    try:
        attempt = await db.assessment_attempts.find_one({"_id": ObjectId(attempt_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid attempt ID")
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    if attempt["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this attempt")
    
    # Check if expired
    now = utcnow()
    if attempt["status"] == "in_progress" and now > attempt["expires_at"]:
        await db.assessment_attempts.update_one(
            {"_id": attempt["_id"]},
            {"$set": {"status": "expired", "submitted_at": now}}
        )
        raise HTTPException(status_code=410, detail="Assessment attempt has expired")
    
    # Fetch assessment and questions
    assessment = await db.skill_assessments.find_one({"_id": ObjectId(attempt["assessment_id"])})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    questions = assessment.get("questions", [])
    
    # Prepare response without correct answers
    response_questions = []
    for q in questions:
        q_dict = {
            "id": q.get("id"),
            "text": q.get("text"),
            "options": q.get("options", []),
            "difficulty": q.get("difficulty", "medium"),
        }
        response_questions.append(q_dict)
    
    result = {
        "attempt_id": str(attempt["_id"]),
        "assessment_id": attempt["assessment_id"],
        "status": attempt["status"],
        "started_at": attempt["started_at"].isoformat(),
        "expires_at": attempt["expires_at"].isoformat(),
        "time_remaining_seconds": int((attempt["expires_at"] - now).total_seconds()),
        "questions": response_questions,
        "saved_answers": attempt.get("answers", {}),
    }
    
    return result


# ────────────────────────────────────────────────────────────────────────────
# SAVE ANSWER DURING ATTEMPT
# ────────────────────────────────────────────────────────────────────────────

@router.post("/attempts/{attempt_id}/answer")
async def save_answer(
    attempt_id: str,
    body: dict,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Save an answer during assessment (auto-save)."""
    user_id = str(user["_id"])
    question_id = body.get("question_id")
    selected_option_id = body.get("selected_option_id")
    
    if not question_id or not selected_option_id:
        raise HTTPException(status_code=400, detail="Missing question_id or selected_option_id")
    
    try:
        attempt = await db.assessment_attempts.find_one({"_id": ObjectId(attempt_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid attempt ID")
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    if attempt["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if attempt["status"] != "in_progress":
        raise HTTPException(status_code=410, detail="Assessment attempt is not in progress")
    
    # Check expiration
    now = utcnow()
    if now > attempt["expires_at"]:
        await db.assessment_attempts.update_one(
            {"_id": attempt["_id"]},
            {"$set": {"status": "expired"}}
        )
        raise HTTPException(status_code=410, detail="Assessment attempt has expired")
    
    # Save answer
    await db.assessment_attempts.update_one(
        {"_id": attempt["_id"]},
        {
            "$set": {
                f"answers.{question_id}": selected_option_id,
                "last_activity": now,
            }
        }
    )
    
    logger.info(f"Answer saved for attempt {attempt_id}, question {question_id}")
    
    return {"success": True, "message": "Answer saved"}


# ────────────────────────────────────────────────────────────────────────────
# SUBMIT ASSESSMENT
# ────────────────────────────────────────────────────────────────────────────

@router.post("/attempts/{attempt_id}/submit")
async def submit_assessment(
    attempt_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Submit assessment attempt and calculate results."""
    user_id = str(user["_id"])
    
    try:
        attempt = await db.assessment_attempts.find_one({"_id": ObjectId(attempt_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid attempt ID")
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    if attempt["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if attempt["status"] != "in_progress":
        raise HTTPException(status_code=410, detail="Attempt is not in progress")
    
    # Fetch assessment
    assessment = await db.skill_assessments.find_one({"_id": ObjectId(attempt["assessment_id"])})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    now = utcnow()
    questions = assessment.get("questions", [])
    saved_answers = attempt.get("answers", {})
    
    # Score the assessment
    correct_count = 0
    total_points = 0
    earned_points = 0
    
    for q in questions:
        question_id = q.get("id")
        correct_option_id = q.get("correct_option_id")
        points = q.get("points", 1)
        
        total_points += points
        
        selected_option = saved_answers.get(question_id)
        if selected_option == correct_option_id:
            correct_count += 1
            earned_points += points
    
    # Calculate percentage and proficiency
    percentage = int(earned_points / total_points * 100) if total_points else 0
    proficiency_level = _proficiency_level(percentage)
    passed = percentage >= 50
    
    # Create result record
    result_doc = {
        "user_id": user_id,
        "attempt_id": str(attempt["_id"]),
        "assessment_id": str(attempt["assessment_id"]),
        "skill_id": attempt.get("skill_id", ""),
        "skill_name": attempt.get("skill_name", ""),
        "score": earned_points,
        "total": total_points,
        "percentage": percentage,
        "correct_answers": correct_count,
        "total_questions": len(questions),
        "proficiency_level": proficiency_level,
        "passed": passed,
        "submitted_at": now,
        "completed_at": now,
    }
    
    result = await db.assessment_results.insert_one(result_doc)
    result_doc["_id"] = result.inserted_id
    
    # Mark attempt as completed
    await db.assessment_attempts.update_one(
        {"_id": attempt["_id"]},
        {
            "$set": {
                "status": "completed",
                "submitted_at": now,
                "completed_at": now,
            }
        }
    )
    
    # Update user_skills proficiency
    skill_id = attempt.get("skill_id")
    if skill_id and ObjectId.is_valid(skill_id):
        skill_doc = await db.skills.find_one({"_id": ObjectId(skill_id)})
        if skill_doc:
            existing_skill = await db.user_skills.find_one({"user_id": user_id, "skill_id": skill_id})
            if existing_skill:
                await db.user_skills.update_one(
                    {"_id": existing_skill["_id"]},
                    {
                        "$set": {
                            "assessment_score": percentage,
                            "proficiency": percentage,
                            "level": proficiency_level,
                            "verified": passed,
                            "last_assessment_at": now,
                            "updated_at": now,
                        }
                    }
                )
            else:
                await db.user_skills.insert_one({
                    "user_id": user_id,
                    "skill_id": skill_id,
                    "skill_name": skill_doc.get("name", attempt.get("skill_name", "")),
                    "category": skill_doc.get("category", ""),
                    "proficiency": percentage,
                    "level": proficiency_level,
                    "verified": passed,
                    "assessment_score": percentage,
                    "source": "assessment",
                    "last_assessment_at": now,
                    "created_at": now,
                    "updated_at": now,
                })
    
    logger.info(f"Assessment submitted: user={user_id}, score={percentage}%, passed={passed}")
    
    return serialize_doc(result_doc)


@router.get("/results/{attempt_id}")
async def get_result(
    attempt_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get assessment result details."""
    user_id = str(user["_id"])
    
    try:
        result = await db.assessment_results.find_one({"attempt_id": attempt_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid attempt ID")
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    if result["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return serialize_doc(result)
