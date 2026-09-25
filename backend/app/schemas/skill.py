from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class SkillCreate(BaseModel):
    name: str
    category: str
    description: str = ""
    demand_score: int = 50
    growth_rate: int = 0
    industries: list[str] = []


class SkillUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    demand_score: int | None = None
    growth_rate: int | None = None
    industries: list[str] | None = None


class SkillResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str = ""
    demand_score: int = 50
    growth_rate: int = 0
    industries: list[str] = []
    industry_relevance: str = "Medium"


class UserSkillCreate(BaseModel):
    skill_id: str
    proficiency: int = 0
    source: str = "self_reported"


class UserSkillUpdate(BaseModel):
    proficiency: int | None = None
    assessment_score: int | None = None
    verified: bool | None = None


class UserSkillResponse(BaseModel):
    id: str
    skill_id: str
    skill_name: str
    category: str
    proficiency: int
    level: str
    verified: bool
    assessment_score: int | None = None
    source: str
