from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.schemas.employment import EmploymentOutcomeCreate, EmploymentOutcomeUpdate
from app.utils.serializer import serialize_doc, serialize_docs
from app.models.base import utcnow
from app.services.email_service import email_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/employment", tags=["Employment"])


@router.get("/me")
async def get_my_outcomes(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    cursor = db.employment_outcomes.find({"trainee_id": user_id}).sort("employment_date", -1)
    docs = await cursor.to_list(length=20)
    return serialize_docs(docs)


@router.post("", status_code=201)
async def create_outcome(
    body: EmploymentOutcomeCreate,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    now = utcnow()
    doc = {
        "trainee_id": user_id,
        **body.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    result = await db.employment_outcomes.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Update trainee employment status
    if body.employer_name:
        await db.trainee_profiles.update_one(
            {"user_id": user_id},
            {"$set": {
                "employment_status": "Employed",
                "company": body.employer_name,
                "job_role": body.job_title,
                "salary": f"₹{body.salary:.1f} LPA" if body.salary else None,
                "updated_at": now,
            }},
        )
    email_service.send_employment_outcome_email(background_tasks, user.get("email"), user.get("name"),
        {"Company": body.employer_name, "Role": body.job_title, "Salary": body.salary,
         "Employment Date": body.employment_date}, user_id)
    return serialize_doc(doc)


@router.put("/{outcome_id}")
async def update_outcome(
    outcome_id: str,
    body: EmploymentOutcomeUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    update["updated_at"] = utcnow()
    result = await db.employment_outcomes.find_one_and_update(
        {"_id": ObjectId(outcome_id)}, {"$set": update}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Outcome not found")
    return serialize_doc(result)


@router.get("/{trainee_id}")
async def get_trainee_outcomes(
    trainee_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if str(user["_id"]) != trainee_id and user.get("role") not in ("GOVERNMENT_ADMIN", "SUPER_ADMIN"):
        raise HTTPException(status_code=403, detail="Forbidden")
    cursor = db.employment_outcomes.find({"trainee_id": trainee_id}).sort("employment_date", -1)
    docs = await cursor.to_list(length=20)
    return serialize_docs(docs)
