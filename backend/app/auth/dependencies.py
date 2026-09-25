from __future__ import annotations
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.auth.jwt import decode_token
from app.database.connection import get_db

_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user["id"] = str(user["_id"])
    return user


def require_role(*roles: str):
    async def _check(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {list(roles)}",
            )
        return user
    return _check


def require_trainee():
    return require_role("TRAINEE")


def require_employer():
    return require_role("EMPLOYER")


def require_institute():
    return require_role("TRAINING_INSTITUTE")


def require_government_admin():
    return require_role("GOVERNMENT_ADMIN", "SUPER_ADMIN")


def require_super_admin():
    return require_role("SUPER_ADMIN")


# Optional auth — returns user dict or None
_bearer_optional = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_optional),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict | None:
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
# dummy change 9
