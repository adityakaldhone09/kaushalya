from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class EmploymentOutcomeCreate(BaseModel):
    training_program_id: str | None = None
    employer_name: str = ""
    job_title: str = ""
    salary: float | None = None
    employment_type: str = "Full-time"
    location: str = ""
    employment_date: str = ""
    source: str = "self_reported"


class EmploymentOutcomeUpdate(BaseModel):
    employer_name: str | None = None
    job_title: str | None = None
    salary: float | None = None
    employment_type: str | None = None
    location: str | None = None
    retention_6_months: bool | None = None
    retention_12_months: bool | None = None
    career_progression: str | None = None


class EmploymentOutcomeResponse(BaseModel):
    id: str
    trainee_id: str
    training_program_id: str | None = None
    employer_name: str = ""
    job_title: str = ""
    salary: float | None = None
    employment_type: str = "Full-time"
    location: str = ""
    employment_date: str = ""
    retention_6_months: bool | None = None
    retention_12_months: bool | None = None
    career_progression: str = ""
    source: str = "self_reported"
