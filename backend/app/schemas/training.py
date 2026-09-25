from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class TrainingProgramCreate(BaseModel):
    name: str
    institute: str
    description: str = ""
    duration: str = ""
    mode: str = "Hybrid"
    location: str = ""
    industry: str = ""
    skills: list[str] = []
    capacity: int = 50


class TrainingProgramUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration: str | None = None
    mode: str | None = None
    location: str | None = None
    industry: str | None = None
    skills: list[str] | None = None
    capacity: int | None = None
    status: str | None = None


class TrainingProgramResponse(BaseModel):
    id: str
    name: str
    institute: str
    description: str = ""
    duration: str = ""
    mode: str = "Hybrid"
    location: str = ""
    industry: str = ""
    skills: list[str] = []
    capacity: int = 50
    enrolled: int = 0
    completion_rate: int = 0
    placement_rate: int = 0
    impact_score: int = 0
    salary: str = "Pending outcomes"
    status: str = "active"


class EnrollmentCreate(BaseModel):
    program_id: str


class EnrollmentUpdate(BaseModel):
    status: str  # ENROLLED, IN_PROGRESS, COMPLETED, DROPPED


class EnrollmentResponse(BaseModel):
    id: str
    trainee_id: str
    program_id: str
    program_name: str = ""
    status: str
    enrolled_at: str
    completed_at: str | None = None


class CertificationCreate(BaseModel):
    name: str
    issuer: str
    program_id: str | None = None
    issue_date: str = ""
    verification_url: str = ""


class CertificationResponse(BaseModel):
    id: str
    user_id: str
    name: str
    issuer: str
    program_id: str | None = None
    issue_date: str = ""
    verified: bool = False
    verification_url: str = ""
