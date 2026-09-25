from __future__ import annotations
from pydantic import BaseModel


class CareerAdviceRequest(BaseModel):
    trainee_id: str
    question: str


class CareerAdviceResponse(BaseModel):
    answer: str
    sources: list[str] = []
    next_steps: list[str] = []
    is_ai_generated: bool = False


class SkillGapExplainRequest(BaseModel):
    trainee_id: str
    target_role: str


class DistrictInsightRequest(BaseModel):
    district: str


class ProgramInsightRequest(BaseModel):
    program_id: str


class AiInsightResponse(BaseModel):
    summary: str
    key_points: list[str] = []
    recommendations: list[str] = []
    priority: str = "medium"
    is_ai_generated: bool = False


class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    is_ai_generated: bool = False
