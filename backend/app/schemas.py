from typing import List, Optional
from pydantic import BaseModel


class ResearchRequest(BaseModel):
    case_id: Optional[str] = None
    source: Optional[str] = None
    text: str
    metadata: Optional[dict] = None


class Citation(BaseModel):
    title: str
    citation: Optional[str] = None
    url: Optional[str] = None


class ResearchResponse(BaseModel):
    issues: List[str]
    citations: List[Citation]
    suggested_actions: List[str]
    brief: Optional[str] = None


class CommunicationRequest(BaseModel):
    case_id: Optional[str] = None
    client_name: Optional[str] = None
    recipient_contact: Optional[str] = None
    tone: Optional[str] = "empathetic"  # e.g., empathetic, neutral, formal
    purpose: Optional[str] = None  # e.g., scheduling, status update, request for records
    text: str  # raw context / message from case file


class CommunicationResponse(BaseModel):
    draft_message: str
    subject: Optional[str] = None
    suggested_followups: List[str]
