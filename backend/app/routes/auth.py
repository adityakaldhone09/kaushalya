from __future__ import annotations
import logging
import secrets
import hashlib
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.config.settings import get_settings
from app.schemas.auth import RegisterRequest, LoginRequest, GoogleLoginRequest, TokenResponse, UserResponse, VerifyEmailRequest, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest, ResendVerificationRequest
from app.models.base import utcnow
from app.services.email_service import email_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


def _user_to_response(user: dict) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        name=user.get("name", ""),
        email=user.get("email", ""),
        role=user.get("role", "TRAINEE"),
        organization=user.get("organization"),
        created_at=str(user.get("created_at", "")),
        is_verified=user.get("email_verified", user.get("is_verified", False)),
    )


def _make_token(user: dict) -> TokenResponse:
    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    token = create_access_token(
        {"user_id": str(user["_id"]), "email": user["email"], "role": user["role"]},
        timedelta(minutes=expire_minutes),
    )
    return TokenResponse(
        access_token=token,
        expires_in=expire_minutes * 60,
        user=_user_to_response(user),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, background_tasks: BackgroundTasks, db: AsyncIOMotorDatabase = Depends(get_db)):
    if body.role not in ("TRAINEE", "EMPLOYER", "TRAINING_INSTITUTE"):
        raise HTTPException(status_code=403, detail="This role must be provisioned by an administrator")
    existing = await db.users.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    now = utcnow()
    raw_token = secrets.token_urlsafe(32)
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()

    user_doc = {
        "name": body.name,
        "email": body.email.lower(),
        "password_hash": hash_password(body.password),
        "role": body.role,
        "organization": body.organization,
        "is_active": True,
        "auth_provider": "local",
        "google_id": None,
        "profile_image": None,
        "email_verified": False,
        "is_verified": False,
        "verification_token_hash": hashed_token,
        "verification_token_expires": now + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES),
        "verification_last_sent_at": now,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    # Create role-specific profile
    if body.role == "TRAINEE":
        await db.trainee_profiles.insert_one({
            "user_id": str(result.inserted_id),
            "name": body.name,
            "email": body.email.lower(),
            "phone": "",
            "district": "",
            "state": "Maharashtra",
            "education": "",
            "specialization": "",
            "employment_status": "Open to work",
            "experience": "",
            "target_career": "",
            "profile_completion": 10,
            "created_at": now,
            "updated_at": now,
        })
    elif body.role == "EMPLOYER":
        await db.employers.insert_one({
            "user_id": str(result.inserted_id),
            "company_name": body.organization or "",
            "industry": "",
            "location": "",
            "website": "",
            "description": "",
            "size": "",
            "verified": False,
            "created_at": now,
        })
    elif body.role == "TRAINING_INSTITUTE":
        await db.training_institutes.insert_one({
            "user_id": str(result.inserted_id),
            "name": body.organization or body.name,
            "location": {"district": "", "state": "Maharashtra"},
            "accredited": False,
            "created_at": now,
        })

    logger.info("New user registered: %s (%s)", body.email, body.role)
    
    # Send welcome and verification emails
    email_service.send_welcome_email(background_tasks, body.email.lower(), body.name, str(result.inserted_id))
    email_service.send_verification_email(background_tasks, body.email.lower(), body.name, raw_token, str(result.inserted_id))

    return _make_token(user_doc)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await db.users.find_one({"email": body.email.lower()})
    if not user or not user.get("password_hash") or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    logger.info("User logged in: %s", body.email)
    return _make_token(user)


@router.post("/google", response_model=TokenResponse)
async def google_login(body: GoogleLoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Exchange a Google Identity Services ID token for a KAUSHALYA JWT."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google sign-in is not configured")
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token
        payload = id_token.verify_oauth2_token(body.credential, Request(), settings.GOOGLE_CLIENT_ID)
    except Exception:
        logger.warning("Google sign-in rejected")
        raise HTTPException(status_code=401, detail="Invalid Google credential")

    google_id = payload.get("sub")
    email = str(payload.get("email", "")).lower()
    if not google_id or not email or not payload.get("email_verified", False):
        raise HTTPException(status_code=401, detail="Google account email is not verified")

    user = await db.users.find_one({"google_id": google_id})
    if user is None:
        user = await db.users.find_one({"email": email})
        if user:
            await db.users.update_one({"_id": user["_id"]}, {"$set": {
                "google_id": google_id, "auth_provider": "hybrid", "email_verified": True,
                "is_verified": True, "profile_image": payload.get("picture"), "updated_at": utcnow(),
            }})
            user = await db.users.find_one({"_id": user["_id"]})
        else:
            now = utcnow()
            doc = {"name": payload.get("name") or email.split("@", 1)[0], "email": email,
                   "role": body.role, "organization": None, "is_active": True,
                   "auth_provider": "google", "google_id": google_id, "profile_image": payload.get("picture"),
                   "email_verified": True, "is_verified": True, "created_at": now, "updated_at": now}
            result = await db.users.insert_one(doc)
            doc["_id"] = result.inserted_id
            if body.role == "TRAINEE":
                await db.trainee_profiles.insert_one({"user_id": str(result.inserted_id), "name": doc["name"],
                    "email": email, "phone": "", "district": "", "state": "Maharashtra", "education": "",
                    "employment_status": "Open to work", "profile_completion": 10, "created_at": now, "updated_at": now})
            user = doc
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account disabled")
    return _make_token(user)


@router.get("/me", response_model=UserResponse)
async def me(user: dict = Depends(get_current_user)):
    return _user_to_response(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(user: dict = Depends(get_current_user)):
    return _make_token(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(user: dict = Depends(get_current_user)):
    return None

@router.post("/verify-email")
async def verify_email(body: VerifyEmailRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    hashed_token = hashlib.sha256(body.token.encode()).hexdigest()
    user = await db.users.find_one({"verification_token_hash": hashed_token})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    if user.get("verification_token_expires") and user["verification_token_expires"] < utcnow():
        raise HTTPException(status_code=400, detail="Verification token has expired")
    
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"email_verified": True, "is_verified": True, "updated_at": utcnow()},
         "$unset": {"verification_token_hash": "", "verification_token_expires": ""}}
    )
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification(body: ResendVerificationRequest, background_tasks: BackgroundTasks, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await db.users.find_one({"email": body.email.lower()})
    if not user or user.get("email_verified", user.get("is_verified", False)):
        return {"message": "If the email exists and is unverified, a link has been sent."}
    last_sent = user.get("verification_last_sent_at")
    if last_sent and last_sent > utcnow() - timedelta(minutes=1):
        return {"message": "If the email exists and is unverified, a link has been sent."}
    
    raw_token = secrets.token_urlsafe(32)
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
    
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"verification_token_hash": hashed_token,
                  "verification_token_expires": utcnow() + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES),
                  "verification_last_sent_at": utcnow()}}
    )
    email_service.send_verification_email(background_tasks, user["email"], user["name"], raw_token, str(user["_id"]))
    return {"message": "If the email exists and is unverified, a link has been sent."}


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await db.users.find_one({"email": body.email.lower()})
    if not user:
        return {"message": "If that email is registered, a reset link will be sent."}
    
    raw_token = secrets.token_urlsafe(32)
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
    
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"reset_token_hash": hashed_token,
                  "reset_token_expires": utcnow() + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)}}
    )
    email_service.send_password_reset_email(background_tasks, user["email"], user["name"], raw_token, str(user["_id"]))
    return {"message": "If that email is registered, a reset link will be sent."}

@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, background_tasks: BackgroundTasks, db: AsyncIOMotorDatabase = Depends(get_db)):
    hashed_token = hashlib.sha256(body.token.encode()).hexdigest()
    user = await db.users.find_one({"reset_token_hash": hashed_token})
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    if user.get("reset_token_expires") and user["reset_token_expires"] < utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"password_hash": hash_password(body.new_password), "updated_at": utcnow(),
                     "auth_provider": "hybrid" if user.get("google_id") else "local"},
            "$unset": {"reset_token_hash": "", "reset_token_expires": ""}
        }
    )
    email_service.send_password_changed_email(background_tasks, user["email"], user.get("name", "there"), str(user["_id"]))
    return {"message": "Password has been reset successfully"}


@router.post("/change-password")
async def change_password(body: ChangePasswordRequest, background_tasks: BackgroundTasks,
                          user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    if not user.get("password_hash") or not verify_password(body.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    await db.users.update_one({"_id": user["_id"]}, {"$set": {
        "password_hash": hash_password(body.new_password), "updated_at": utcnow(),
        "auth_provider": "hybrid" if user.get("google_id") else "local"}})
    email_service.send_password_changed_email(background_tasks, user["email"], user.get("name", "there"), str(user["_id"]))
    return {"message": "Password changed successfully"}
