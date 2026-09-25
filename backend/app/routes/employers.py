from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.schemas.employer import EmployerProfileUpdate
from app.utils.serializer import serialize_doc
from app.models.base import utcnow

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/employers", tags=["Employers"])


@router.get("/me")
async def get_my_employer_profile(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    profile = await db.employers.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")
    return serialize_doc(profile)


@router.put("/me")
async def update_my_employer_profile(
    body: EmployerProfileUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(user["_id"])
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    update["updated_at"] = utcnow()
    result = await db.employers.find_one_and_update(
        {"user_id": user_id}, {"$set": update}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Employer profile not found")
    return serialize_doc(result)
