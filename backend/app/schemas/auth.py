from __future__ import annotations
from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal


UserRole = Literal["TRAINEE", "EMPLOYER", "TRAINING_INSTITUTE", "GOVERNMENT_ADMIN", "SUPER_ADMIN"]


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = "TRAINEE"
    organization: str | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8 or not any(c.isupper() for c in v) or not any(c.islower() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must be 8+ characters with uppercase, lowercase, and a number")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    credential: str
    role: Literal["TRAINEE", "EMPLOYER", "TRAINING_INSTITUTE"] = "TRAINEE"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    organization: str | None = None
    created_at: str | None = None
    is_verified: bool = False

class VerifyEmailRequest(BaseModel):
    token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8 or not any(c.isupper() for c in v) or not any(c.islower() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must be 8+ characters with uppercase, lowercase, and a number")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8 or not any(c.isupper() for c in v) or not any(c.islower() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must be 8+ characters with uppercase, lowercase, and a number")
        return v

TokenResponse.model_rebuild()
