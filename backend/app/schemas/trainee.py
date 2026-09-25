from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional


class LocationSchema(BaseModel):
    district: str = ""
    state: str = "Maharashtra"
    city: str = ""


class EducationSchema(BaseModel):
    degree: str = ""
    field: str = ""
    institution: str = ""
    graduation_year: int | None = None


class TraineeSkillItem(BaseModel):
    skill: str
    skill_id: str | None = None
    category: str = ""
    proficiency: int = 0
    level: str = "Beginner"
    verified: bool = False
    assessment_score: int | None = None


class TraineeProfileCreate(BaseModel):
    name: str
    phone: str = ""
    location: LocationSchema = LocationSchema()
    education: EducationSchema = EducationSchema()
    employment_status: str = "Open to work"
    experience: str = ""
    target_career: str = ""


class TraineeProfileUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    district: str | None = None
    state: str | None = None
    education: str | None = None
    specialization: str | None = None
    target_career: str | None = None
    employment_status: str | None = None
    experience: str | None = None
    company: str | None = None
    job_role: str | None = None
    salary: str | None = None


class TraineeResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str = ""
    district: str = ""
    state: str = "Maharashtra"
    education: str = ""
    specialization: str = ""
    employment_status: str = "Open to work"
    company: str | None = None
    job_role: str | None = None
    salary: str | None = None
    experience: str = ""
    profile_completion: int = 0
    employability_score: int = 0
    score_class: str = "Medium"
    target_career: str = ""
    skills: list[TraineeSkillItem] = []
