from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class RouteType(str, Enum):
    SALES = "sales"
    GENERAL = "general"

class QuestionRequest(BaseModel):
    question: str

class AIResponse(BaseModel):
    answer: str
    route_type: Optional[str] = None
    processing_time: Optional[float] = None

class RouteDecision(BaseModel):
    route_type: RouteType
    confidence: float
    reasoning: Optional[str] = None

class SalesRepData(BaseModel):
    id: str
    name: str
    role: str
    region: str
    skills: List[str]
    clients: Optional[List[Dict[str, Any]]] = None
    deals: Optional[List[Dict[str, Any]]] = None
