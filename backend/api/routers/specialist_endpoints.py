"""
AI Specialist Direct Endpoints

Direct API endpoints for each AI specialist agent.
These can be called independently or through the orchestrator.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

from app.specialists.records_wrangler import RecordsWrangler
from app.specialists.voice_scheduler import VoiceScheduler
from app.specialists.evidence_sorter import EvidenceSorter
from app.specialists.legal_researcher import LegalResearcher
from app.specialists.client_communication import ClientCommunicator
from app.specialists.gemini_adapter import GeminiAdapter

router = APIRouter()

# Initialize LLM adapter - prefer Gemini, fallback to mock
def get_llm_adapter():
    """Get the configured LLM adapter based on available API keys"""
    google_api_key = os.getenv("GOOGLE_AI_API_KEY")

    if google_api_key:
        print("✓ Using Gemini as LLM provider")
        return GeminiAdapter(api_key=google_api_key)

    print("⚠ No AI API key found - using mock responses")
    return None  # Will use mock adapter

# Initialize specialists with Gemini
llm_adapter = get_llm_adapter()
records_wrangler = RecordsWrangler(llm_adapter=llm_adapter)
voice_scheduler = VoiceScheduler(llm_adapter=llm_adapter)
evidence_sorter = EvidenceSorter(llm_adapter=llm_adapter)
legal_researcher = LegalResearcher(llm_adapter=llm_adapter)
client_communicator = ClientCommunicator(llm_adapter=llm_adapter)


# Request Models
class RecordsAnalysisRequest(BaseModel):
    """Request for records analysis"""
    text: str = Field(..., description="Text to analyze for record needs")
    case_id: Optional[str] = Field(None, description="Case ID")
    existing_records: Optional[List[str]] = Field(default_factory=list, description="Records already on file")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "I had an MRI at City Hospital last week and saw Dr. Johnson. The bill was $3,500.",
                "case_id": "CASE-2024-001",
                "existing_records": ["Initial consultation notes"]
            }
        }


class SchedulingRequest(BaseModel):
    """Request for scheduling assistance"""
    text: str = Field(..., description="Text containing scheduling request")
    case_id: Optional[str] = Field(None, description="Case ID")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "We need to schedule the deposition for next week, preferably Tuesday or Wednesday afternoon.",
                "case_id": "CASE-2024-001"
            }
        }


class DocumentAnalysisRequest(BaseModel):
    """Request for document analysis"""
    filename: str = Field(..., description="Document filename")
    text_content: Optional[str] = Field(None, description="Extracted text content")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    case_id: Optional[str] = Field(None, description="Case ID")

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "medical_records_dr_smith.pdf",
                "text_content": "Patient: John Doe. Date: 01/15/2024. Diagnosis: Lumbar sprain...",
                "file_size": 245000,
                "case_id": "CASE-2024-001"
            }
        }


class BatchDocumentRequest(BaseModel):
    """Request for batch document processing"""
    documents: List[Dict[str, Any]] = Field(..., description="List of documents to process")
    case_id: Optional[str] = Field(None, description="Case ID")


class LegalResearchRequest(BaseModel):
    """Request for legal research"""
    text: str = Field(..., description="Text to research")
    case_id: Optional[str] = Field(None, description="Case ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CommunicationDraftRequest(BaseModel):
    """Request for client communication draft"""
    client_name: Optional[str] = Field(None, description="Client name")
    purpose: Optional[str] = Field(None, description="Purpose of communication")
    text: str = Field(..., description="Context for the communication")


# Records Wrangler Endpoints
@router.post("/records-wrangler/analyze", status_code=status.HTTP_200_OK)
async def analyze_records_needs(request: RecordsAnalysisRequest):
    """
    Analyze text to identify record needs and draft request letters

    Returns:
        - Identified medical providers
        - Missing records
        - Billing items
        - Draft record request letters
    """
    try:
        result = await records_wrangler.analyze_records_needs(
            text=request.text,
            case_id=request.case_id,
            existing_records=request.existing_records
        )

        return {
            "status": "success",
            "specialist": "Records Wrangler",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in records analysis: {str(e)}"
        )


@router.post("/records-wrangler/draft-outreach", status_code=status.HTTP_200_OK)
async def draft_provider_outreach(
    provider_name: str,
    record_types: List[str],
    case_id: Optional[str] = None,
    patient_name: Optional[str] = None
):
    """
    Draft a medical provider outreach letter
    """
    try:
        result = await records_wrangler.draft_provider_outreach(
            provider_name=provider_name,
            record_types=record_types,
            case_id=case_id,
            patient_name=patient_name
        )

        return {
            "status": "success",
            "specialist": "Records Wrangler",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error drafting outreach: {str(e)}"
        )


# Voice Scheduler Endpoints
@router.post("/voice-scheduler/parse-request", status_code=status.HTTP_200_OK)
async def parse_scheduling_request(request: SchedulingRequest):
    """
    Parse a scheduling request from text

    Returns:
        - Appointment type
        - Date/time preferences
        - Required participants
        - Urgency level
    """
    try:
        result = await voice_scheduler.parse_scheduling_request(
            text=request.text,
            case_id=request.case_id
        )

        return {
            "status": "success",
            "specialist": "Voice Scheduler",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing scheduling request: {str(e)}"
        )


@router.post("/voice-scheduler/generate-options", status_code=status.HTTP_200_OK)
async def generate_scheduling_options(
    appointment_type: str,
    duration_minutes: int = 60
):
    """
    Generate available scheduling options
    """
    try:
        result = await voice_scheduler.generate_scheduling_options(
            appointment_type=appointment_type,
            duration_minutes=duration_minutes
        )

        return {
            "status": "success",
            "specialist": "Voice Scheduler",
            "available_slots": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating options: {str(e)}"
        )


@router.post("/voice-scheduler/draft-message", status_code=status.HTTP_200_OK)
async def draft_scheduling_message(
    recipient_name: Optional[str],
    appointment_type: str,
    proposed_slot_ids: List[str],
    case_id: Optional[str] = None
):
    """
    Draft a scheduling coordination message
    """
    try:
        # Generate slots (in production, would retrieve from database)
        all_slots = await voice_scheduler.generate_scheduling_options(appointment_type)
        proposed_slots = [s for s in all_slots if s["slot_id"] in proposed_slot_ids]

        result = await voice_scheduler.draft_scheduling_message(
            recipient_name=recipient_name,
            appointment_type=appointment_type,
            proposed_slots=proposed_slots,
            case_id=case_id
        )

        return {
            "status": "success",
            "specialist": "Voice Scheduler",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error drafting message: {str(e)}"
        )


# Evidence Sorter Endpoints
@router.post("/evidence-sorter/analyze-document", status_code=status.HTTP_200_OK)
async def analyze_document(request: DocumentAnalysisRequest):
    """
    Analyze and classify a single document

    Returns:
        - Document classification
        - Metadata extraction
        - Suggested tags
        - Filing recommendation
    """
    try:
        result = await evidence_sorter.analyze_document(
            filename=request.filename,
            text_content=request.text_content,
            file_size=request.file_size,
            case_id=request.case_id
        )

        return {
            "status": "success",
            "specialist": "Evidence Sorter",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing document: {str(e)}"
        )


@router.post("/evidence-sorter/process-batch", status_code=status.HTTP_200_OK)
async def process_document_batch(request: BatchDocumentRequest):
    """
    Process multiple documents at once

    Returns:
        - Batch processing results
        - Category breakdown
        - Duplicate detection
        - Summary statistics
    """
    try:
        result = await evidence_sorter.process_batch(
            documents=request.documents,
            case_id=request.case_id
        )

        return {
            "status": "success",
            "specialist": "Evidence Sorter",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing batch: {str(e)}"
        )


@router.post("/evidence-sorter/salesforce-payload", status_code=status.HTTP_200_OK)
async def generate_salesforce_payload(document_analysis: Dict[str, Any]):
    """
    Generate Salesforce-compatible upload payload
    """
    try:
        payload = evidence_sorter.generate_salesforce_payload(document_analysis)

        return {
            "status": "success",
            "specialist": "Evidence Sorter",
            "salesforce_payload": payload
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Salesforce payload: {str(e)}"
        )


# Legal Researcher Endpoints
@router.post("/legal-researcher/analyze", status_code=status.HTTP_200_OK)
async def legal_research_analysis(request: LegalResearchRequest):
    """
    Conduct legal research analysis

    Returns:
        - Identified legal issues
        - Relevant citations
        - Suggested actions
        - Research brief
    """
    try:
        result = await legal_researcher.analyze(
            text=request.text,
            metadata=request.metadata
        )

        return {
            "status": "success",
            "specialist": "Legal Researcher",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in legal research: {str(e)}"
        )


# Client Communication Guru Endpoints
@router.post("/client-communication/draft", status_code=status.HTTP_200_OK)
async def draft_client_communication(request: CommunicationDraftRequest):
    """
    Draft client communication message

    Returns:
        - Draft message
        - Subject line
        - Suggested follow-ups
    """
    try:
        result = await client_communicator.draft(
            client_name=request.client_name,
            purpose=request.purpose,
            text=request.text
        )

        return {
            "status": "success",
            "specialist": "Client Communication Guru",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error drafting communication: {str(e)}"
        )


# Specialist Information Endpoints
@router.get("/specialists", status_code=status.HTTP_200_OK)
async def get_all_specialists():
    """
    Get information about all available specialists
    """
    return {
        "specialists": {
            "records_wrangler": {
                "name": "Records Wrangler",
                "description": "Pulls missing bills or records from client messages",
                "capabilities": [
                    "Identify medical providers",
                    "Detect missing records",
                    "Draft HIPAA-compliant record requests",
                    "Track billing items"
                ],
                "endpoints": [
                    "/specialists/records-wrangler/analyze",
                    "/specialists/records-wrangler/draft-outreach"
                ]
            },
            "voice_scheduler": {
                "name": "Voice Bot Scheduler",
                "description": "Coordinates depositions, mediations, and appointments",
                "capabilities": [
                    "Parse scheduling requests",
                    "Generate time slot options",
                    "Draft scheduling messages",
                    "Create confirmation messages"
                ],
                "endpoints": [
                    "/specialists/voice-scheduler/parse-request",
                    "/specialists/voice-scheduler/generate-options",
                    "/specialists/voice-scheduler/draft-message"
                ]
            },
            "evidence_sorter": {
                "name": "Evidence Sorter",
                "description": "Extracts and labels attachments for case management",
                "capabilities": [
                    "Classify documents automatically",
                    "Extract metadata",
                    "Detect duplicates",
                    "Generate Salesforce payloads"
                ],
                "endpoints": [
                    "/specialists/evidence-sorter/analyze-document",
                    "/specialists/evidence-sorter/process-batch",
                    "/specialists/evidence-sorter/salesforce-payload"
                ]
            },
            "legal_researcher": {
                "name": "Legal Researcher",
                "description": "Finds supporting verdicts and citations",
                "capabilities": [
                    "Identify legal issues",
                    "Find relevant citations",
                    "Suggest legal strategies",
                    "Draft research briefs"
                ],
                "endpoints": [
                    "/specialists/legal-researcher/analyze"
                ]
            },
            "client_communication_guru": {
                "name": "Client Communication Guru",
                "description": "Drafts clear, empathetic messages to clients",
                "capabilities": [
                    "Draft client messages",
                    "Generate subject lines",
                    "Suggest follow-ups",
                    "Maintain empathetic tone"
                ],
                "endpoints": [
                    "/specialists/client-communication/draft"
                ]
            }
        }
    }


@router.get("/specialists/{specialist_name}/info", status_code=status.HTTP_200_OK)
async def get_specialist_info(specialist_name: str):
    """
    Get detailed information about a specific specialist
    """
    specialists_info = await get_all_specialists()

    if specialist_name not in specialists_info["specialists"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specialist '{specialist_name}' not found"
        )

    return {
        "specialist": specialist_name,
        "info": specialists_info["specialists"][specialist_name]
    }
