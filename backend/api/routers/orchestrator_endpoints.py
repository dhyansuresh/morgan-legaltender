"""
Orchestrator API Endpoints

Main endpoints for the Tender for Lawyers AI Orchestrator.
These endpoints handle incoming messages, process them, route to specialists,
and manage the human approval workflow.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum

from orchestrator.tender_orchestrator import (
    TenderOrchestrator,
    SourceType,
    ApprovalStatus
)
from orchestrator.advanced_router import TaskRouter

router = APIRouter()

# Initialize orchestrator with Gemini-powered routing
# The orchestrator will automatically use GeminiTaskRouter if use_ai_routing=True
orchestrator = TenderOrchestrator(use_ai_routing=True)


# Request/Response Models
class ProcessInputRequest(BaseModel):
    """Request model for processing input"""
    raw_text: str = Field(..., description="Raw text from email, SMS, transcript, etc.")
    source_type: str = Field(..., description="Type of input source")
    case_id: Optional[str] = Field(None, description="Associated case ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "raw_text": "Hi, I had my MRI done at Dr. Smith's office yesterday. When can I get a copy of those records? Also the bill was $2,500 and I'm not sure if my insurance will cover it. Can we discuss?",
                "source_type": "email",
                "case_id": "CASE-2024-001",
                "metadata": {
                    "sender": "client@example.com",
                    "received_at": "2024-01-15T10:30:00Z"
                }
            }
        }


class ApprovalRequest(BaseModel):
    """Request model for approving/rejecting a proposed action"""
    processing_id: str = Field(..., description="Processing ID from orchestrator")
    task_id: str = Field(..., description="Task ID to approve/reject")
    approval_status: str = Field(..., description="approved or rejected")
    reviewer_notes: Optional[str] = Field(None, description="Optional notes from reviewer")
    modifications: Optional[Dict[str, Any]] = Field(None, description="Optional modifications to the action")


class AttachmentMetadata(BaseModel):
    """Metadata for an attachment"""
    filename: str
    file_size: int
    file_type: str
    content_preview: Optional[str] = None


# Endpoints
@router.post("/process", status_code=status.HTTP_200_OK)
async def process_input(request: ProcessInputRequest):
    """
    Process incoming messy input through the Tender orchestrator

    This is the main entry point for the system. It:
    1. Normalizes messy text from various sources
    2. Extracts entities and structured data
    3. Labels PII/PHI
    4. Detects actionable tasks
    5. Routes tasks to appropriate specialists
    6. Generates proposed actions requiring approval

    Returns:
        Comprehensive analysis with detected tasks, routing decisions,
        and proposed actions pending human approval
    """
    try:
        # Validate source type
        try:
            source_type_enum = SourceType(request.source_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source_type. Must be one of: {[s.value for s in SourceType]}"
            )

        # Process the input
        result = await orchestrator.process_input(
            raw_text=request.raw_text,
            source_type=source_type_enum,
            metadata=request.metadata,
            case_id=request.case_id
        )

        return {
            "status": "success",
            "message": "Input processed successfully",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing input: {str(e)}"
        )


@router.post("/process-with-attachments", status_code=status.HTTP_200_OK)
async def process_with_attachments(
    raw_text: str,
    source_type: str,
    case_id: Optional[str] = None,
    files: List[UploadFile] = File(None)
):
    """
    Process input with file attachments

    Handles messages that include attachments (PDFs, images, etc.)
    """
    try:
        # Validate source type
        try:
            source_type_enum = SourceType(source_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source_type"
            )

        # Process attachments
        attachments = []
        if files:
            for file in files:
                content = await file.read()
                attachments.append({
                    "filename": file.filename,
                    "file_size": len(content),
                    "content_type": file.content_type,
                    "content_preview": content[:500].decode('utf-8', errors='ignore')  # Preview
                })

        # Process the input with attachments
        result = await orchestrator.process_input(
            raw_text=raw_text,
            source_type=source_type_enum,
            case_id=case_id,
            attachments=attachments
        )

        return {
            "status": "success",
            "message": f"Input processed with {len(attachments)} attachment(s)",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing input with attachments: {str(e)}"
        )


@router.get("/processing-history", status_code=status.HTTP_200_OK)
async def get_processing_history(
    case_id: Optional[str] = None,
    limit: int = 50
):
    """
    Get processing history

    Optionally filter by case_id
    """
    try:
        history = orchestrator.get_processing_history(case_id=case_id, limit=limit)

        return {
            "status": "success",
            "total_records": len(history),
            "case_id_filter": case_id,
            "history": history
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving history: {str(e)}"
        )


@router.post("/approve-action", status_code=status.HTTP_200_OK)
async def approve_action(request: ApprovalRequest):
    """
    Approve or reject a proposed action

    This enforces the HUMAN_APPROVAL gate. No actions are taken
    without explicit approval through this endpoint.
    """
    try:
        # Validate approval status
        try:
            approval_enum = ApprovalStatus(request.approval_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="approval_status must be 'approved' or 'rejected'"
            )

        # Record the approval decision
        approval_record = {
            "processing_id": request.processing_id,
            "task_id": request.task_id,
            "approval_status": approval_enum.value,
            "reviewer_notes": request.reviewer_notes,
            "modifications": request.modifications,
            "approved_at": "2024-01-15T12:00:00Z",  # Would use actual timestamp
            "approved_by": "human_reviewer"  # Would use actual user ID
        }

        if approval_enum == ApprovalStatus.APPROVED:
            message = f"Action {request.task_id} approved and queued for execution"
        else:
            message = f"Action {request.task_id} rejected"

        return {
            "status": "success",
            "message": message,
            "approval_record": approval_record,
            "next_steps": (
                ["Execute approved action", "Notify assigned specialist"]
                if approval_enum == ApprovalStatus.APPROVED
                else ["Action canceled", "No further steps required"]
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing approval: {str(e)}"
        )


@router.get("/pending-approvals", status_code=status.HTTP_200_OK)
async def get_pending_approvals(case_id: Optional[str] = None):
    """
    Get all actions pending human approval

    Optionally filter by case_id
    """
    try:
        # In production, would query database for pending approvals
        # For now, return structure
        pending = {
            "total_pending": 0,
            "case_id_filter": case_id,
            "pending_actions": [],
            "summary": {
                "urgent": 0,
                "high_priority": 0,
                "medium_priority": 0,
                "low_priority": 0
            }
        }

        return {
            "status": "success",
            "data": pending
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving pending approvals: {str(e)}"
        )


@router.get("/source-types", status_code=status.HTTP_200_OK)
async def get_supported_source_types():
    """
    Get list of supported input source types
    """
    return {
        "source_types": [source.value for source in SourceType],
        "total": len(SourceType),
        "descriptions": {
            "email": "Email messages from clients or opposing counsel",
            "sms": "Text messages from clients",
            "client_portal": "Messages from client portal",
            "phone_transcript": "Transcripts from phone calls",
            "voicemail": "Transcribed voicemail messages",
            "fax": "Faxed documents (OCR processed)",
            "manual_entry": "Manually entered notes or information"
        }
    }


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_orchestrator_stats():
    """
    Get orchestrator statistics and analytics
    """
    try:
        history = orchestrator.get_processing_history(limit=1000)

        # Calculate statistics
        total_processed = len(history)
        by_source = {}
        total_tasks = 0

        for record in history:
            source = record.get("source_type")
            by_source[source] = by_source.get(source, 0) + 1
            total_tasks += record.get("tasks_detected", 0)

        return {
            "status": "success",
            "statistics": {
                "total_inputs_processed": total_processed,
                "total_tasks_detected": total_tasks,
                "average_tasks_per_input": round(total_tasks / total_processed, 2) if total_processed > 0 else 0,
                "by_source_type": by_source
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating statistics: {str(e)}"
        )


@router.post("/test-input", status_code=status.HTTP_200_OK)
async def test_input(text: str):
    """
    Quick test endpoint to process a simple text input

    Useful for testing and demonstration
    """
    try:
        result = await orchestrator.process_input(
            raw_text=text,
            source_type=SourceType.MANUAL_ENTRY,
            case_id="TEST"
        )

        return {
            "status": "success",
            "summary": {
                "tasks_detected": len(result["detected_tasks"]),
                "entities_found": {k: len(v) for k, v in result["extracted_entities"].items()},
                "pii_phi_detected": bool(result["pii_phi_labels"]["pii"] or result["pii_phi_labels"]["phi"]),
                "approval_required": result["approval_required"]
            },
            "full_result": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing test input: {str(e)}"
        )
