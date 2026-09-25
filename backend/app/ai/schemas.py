from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    reply: str
    intent: str
    sources: Optional[List[str]] = None

class CareerAdviceRequest(BaseModel):
    skills: List[str]
    interests: List[str]

class CareerAdviceResponse(BaseModel):
    recommended_roles: List[str]
    analysis: str
