from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.services.email_service import email_service
from app.schemas.training import (
    TrainingProgramCreate, TrainingProgramUpdate,
    EnrollmentCreate, EnrollmentUpdate,
    CertificationCreate,
)
from app.utils.serializer import serialize_doc, serialize_docs
from app.models.base import utcnow

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Training"])

def _program_doc(doc: dict) -> dict:
    s = serialize_doc(doc) or {}
    return {
        "id": s.get("id", ""),
        "name": s.get("name", ""),
        "institute": s.get("institute", ""),
        "description": s.get("description", ""),
        "duration": s.get("duration", ""),
        "mode": s.get("mode", "Hybrid"),
        "location": s.get("location", ""),
        "industry": s.get("industry", ""),
        "skills": s.get("skills", []),
        "capacity": s.get("capacity", 50),
        "enrolled": s.get("enrolled", 0),
        "completionRate": s.get("completion_rate", 0),
        "placementRate": s.get("placement_rate", 0),
        "impactScore": s.get("impact_score", 0),
        "salary": s.get("salary", "Pending outcomes"),
        "status": s.get("status", "active"),
    }

@router.get("/training-programs")
async def list_programs(
    industry: str = Query(default=""),
    location: str = Query(default=""),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    q: dict = {}
    if industry:
        q["industry"] = {"$regex": industry, "$options": "i"}
    if location:
        q["location"] = {"$regex": location, "$options": "i"}
    cursor = db.training_programs.find(q).sort("placement_rate", -1).limit(50)
    docs = await cursor.to_list(length=50)
    return [_program_doc(d) for d in docs]

@router.get("/training-programs/{program_id}")
async def get_program(program_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db.training_programs.find_one({"_id": ObjectId(program_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Program not found")
    return _program_doc(doc)

@router.post("/training-programs", status_code=201)
async def create_program(
    body: TrainingProgramCreate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = {
        **body.model_dump(),
        "enrolled": 0,
        "completion_rate": 0,
        "placement_rate": 0,
        "impact_score": 0,
        "salary": "Pending outcomes",
        "status": "active",
        "created_by": str(user["_id"]),
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    result = await db.training_programs.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _program_doc(doc)

@router.put("/training-programs/{program_id}")
async def update_program(
    program_id: str,
    body: TrainingProgramUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    update["updated_at"] = utcnow()
    result = await db.training_programs.find_one_and_update(
        {"_id": ObjectId(program_id)}, {"$set": update}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Program not found")
    return _program_doc(result)

@router.delete("/training-programs/{program_id}", status_code=204)
async def delete_program(
    program_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if user.get("role") not in ("SUPER_ADMIN", "GOVERNMENT_ADMIN"):
        raise HTTPException(status_code=403, detail="Admin required")
    await db.training_programs.delete_one({"_id": ObjectId(program_id)})

@router.post("/enrollments", status_code=201)
async def enroll(
    body: EnrollmentCreate,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    program = await db.training_programs.find_one({"_id": ObjectId(body.program_id)})
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    existing = await db.enrollments.find_one({"trainee_id": user_id, "program_id": body.program_id})
    if existing:
        raise HTTPException(status_code=409, detail="Already enrolled")

    now = utcnow()
    doc = {
        "trainee_id": user_id,
        "program_id": body.program_id,
        "program_name": program.get("name", ""),
        "status": "ENROLLED",
        "enrolled_at": now,
        "completed_at": None,
    }
    result = await db.enrollments.insert_one(doc)
    doc["_id"] = result.inserted_id
    await db.training_programs.update_one(
        {"_id": ObjectId(body.program_id)}, {"$inc": {"enrolled": 1}}
    )
    
    email_service.send_training_enrollment_email(background_tasks, user.get("email"), user.get("name"),
        {"Program": program.get("name"), "Institute": program.get("institute"), "Duration": program.get("duration")}, user_id)
    
    return serialize_doc(doc)

@router.get("/enrollments/me")
async def my_enrollments(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    cursor = db.enrollments.find({"trainee_id": user_id})
    docs = await cursor.to_list(length=50)
    return serialize_docs(docs)

@router.put("/enrollments/{enrollment_id}")
async def update_enrollment(
    enrollment_id: str,
    body: EnrollmentUpdate,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    update: dict = {"status": body.status, "updated_at": utcnow()}
    if body.status == "COMPLETED":
        update["completed_at"] = utcnow()
    result = await db.enrollments.find_one_and_update(
        {"_id": ObjectId(enrollment_id)}, {"$set": update}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Enrollment not found")
        
    trainee = await db.users.find_one({"_id": ObjectId(result["trainee_id"])})
    if trainee:
        if body.status == "COMPLETED":
            email_service.send_training_completion_email(background_tasks, trainee.get("email"), trainee.get("name"),
                {"Program": result.get("program_name"), "Skills acquired": result.get("skills", [])}, str(trainee["_id"]))
        
    return serialize_doc(result)

@router.post("/certifications", status_code=201)
async def add_certification(
    body: CertificationCreate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    doc = {
        "user_id": user_id,
        **body.model_dump(),
        "verified": False,
        "created_at": utcnow(),
    }
    result = await db.certifications.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@router.get("/certifications/me")
async def my_certifications(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    cursor = db.certifications.find({"user_id": user_id})
    docs = await cursor.to_list(length=50)
    return serialize_docs(docs)
