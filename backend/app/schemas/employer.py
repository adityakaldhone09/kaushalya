from __future__ import annotations
from pydantic import BaseModel


class EmployerProfileUpdate(BaseModel):
    company_name: str | None = None
    industry: str | None = None
    location: str | None = None
    website: str | None = None
    description: str | None = None
    size: str | None = None


class EmployerProfileResponse(BaseModel):
    id: str
    user_id: str
    company_name: str = ""
    industry: str = ""
    location: str = ""
    website: str = ""
    description: str = ""
    size: str = ""
    verified: bool = False
