from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pydantic import BaseModel, Field
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.models.base import utcnow

router = APIRouter(prefix="/users", tags=["Users"])

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    profile_image: str | None = Field(default=None, max_length=2048)
    location: str | None = Field(default=None, max_length=160)
    education: str | None = Field(default=None, max_length=240)
    professional_information: str | None = Field(default=None, max_length=2000)

def _public_user(user: dict) -> dict:
    return {"id": str(user["_id"]), "name": user.get("name", ""), "email": user.get("email", ""),
            "role": user.get("role", "TRAINEE"), "profile_image": user.get("profile_image"),
            "organization": user.get("organization")}

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return _public_user(user)

@router.put("/me")
async def update_me(body: UserUpdate, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    update["updated_at"] = utcnow()
    await db.users.update_one({"_id": user["_id"]}, {"$set": {k: v for k, v in update.items() if k in ("name", "profile_image", "updated_at")}})
    profile_update = {k: v for k, v in update.items() if k not in ("name", "profile_image", "updated_at")}
    if profile_update and user.get("role") == "TRAINEE":
        await db.trainee_profiles.update_one({"user_id": str(user["_id"])}, {"$set": profile_update})
    refreshed = await db.users.find_one({"_id": user["_id"]})
    return _public_user(refreshed)

@router.get("/{user_id}")
async def get_user(user_id: str, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    if str(user["_id"]) != user_id and user.get("role") not in ("GOVERNMENT_ADMIN", "SUPER_ADMIN"):
        raise HTTPException(status_code=403, detail="Forbidden")
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    return _public_user(target)
