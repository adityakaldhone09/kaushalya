from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class JobCreate(BaseModel):
    title: str
    company: str
    industry: str = ""
    location: str = ""
    job_type: str = "Full-time"
    experience: str = ""
    salary: str = ""
    required_skills: list[str] = []
    deadline: str = ""
    description: str = ""


class JobUpdate(BaseModel):
    title: str | None = None
    industry: str | None = None
    location: str | None = None
    job_type: str | None = None
    experience: str | None = None
    salary: str | None = None
    required_skills: list[str] | None = None
    deadline: str | None = None
    description: str | None = None
    status: str | None = None


class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    industry: str = ""
    location: str = ""
    job_type: str = "Full-time"
    experience: str = ""
    salary: str = ""
    required_skills: list[str] = []
    posted: str = ""
    deadline: str = ""
    applicants: int = 0
    match: int = 0
    status: str = "open"
    employer_id: str = ""


class JobMatchResponse(BaseModel):
    id: str
    title: str
    company: str
    industry: str = ""
    location: str = ""
    job_type: str = "Full-time"
    experience: str = ""
    salary: str = ""
    required_skills: list[str] = []
    posted: str = ""
    deadline: str = ""
    applicants: int = 0
    match: int = 0
    matching_skills: list[str] = []
    missing_skills: list[str] = []
    match_reason: str = ""


class JobApplicationCreate(BaseModel):
    trainee_id: str
    note: str = ""


class JobApplicationResponse(BaseModel):
    id: str
    job_id: str
    trainee_id: str
    status: str = "submitted"
    note: str = ""
    created_at: str
