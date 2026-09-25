from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class EmployabilityBreakdown(BaseModel):
    skills: int = 0
    assessment: int = 0
    training: int = 0
    certifications: int = 0
    experience: int = 0
    demand: int = 0
    profile: int = 0


class EmployabilityScoreResponse(BaseModel):
    score: int
    classification: str
    breakdown: EmployabilityBreakdown


class SkillGapItem(BaseModel):
    skill: str
    category: str
    required_proficiency: int
    current_proficiency: int
    gap: int
    priority: str  # high, medium, low
    status: str  # missing, weak, adequate, strong


class SkillGapResponse(BaseModel):
    overall_match: int
    target_role: str
    matching_skills: list[str]
    weak_skills: list[SkillGapItem]
    missing_skills: list[str]
    priority_skills: list[str]
    recommended_training: list[str]


class SkillGapAnalyzeRequest(BaseModel):
    target_role: str
    target_skills: list[str] = []


class DistrictDigitalTwinResponse(BaseModel):
    district: str
    workforce: dict
    skills: dict
    training: dict
    employment: dict
    industry_demand: dict
    skill_gaps: dict
    forecast: dict
    recommendations: list[str]


class ProgramImpactResponse(BaseModel):
    program_id: str
    program_name: str
    impact_score: int
    classification: str
    metrics: dict
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
