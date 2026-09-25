from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AssessmentQuestionOption(BaseModel):
    id: str
    text: str


class AssessmentQuestion(BaseModel):
    id: str
    text: str
    options: list[AssessmentQuestionOption]
    difficulty: str = "medium"
    points: int = 1


class AssessmentResponse(BaseModel):
    id: str
    skill_id: str
    skill_name: str
    title: str
    description: str = ""
    duration_minutes: int = 30
    total_questions: int = 0
    difficulty: str = "mixed"
    questions: list[AssessmentQuestion] = []


class AssessmentSubmitAnswer(BaseModel):
    question_id: str
    selected_option_id: str


class AssessmentSubmit(BaseModel):
    answers: list[AssessmentSubmitAnswer]


class AssessmentResultResponse(BaseModel):
    id: str
    assessment_id: str
    skill_id: str
    skill_name: str
    score: int
    total: int
    percentage: int
    proficiency_level: str
    passed: bool
    completed_at: str
    employability_score: int | None = None
