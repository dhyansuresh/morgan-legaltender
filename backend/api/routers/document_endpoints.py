"""
Document Upload and Processing API Endpoints

Handles document uploads (PDF, images, Word, Excel) and sends
extracted text to the orchestrator for task detection and routing.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
from typing import Optional, List
from pydantic import BaseModel
import os

from app.services.document_processor import DocumentProcessor
from orchestrator.tender_orchestrator import TenderOrchestrator, SourceType
from orchestrator.advanced_router import TaskRouter

router = APIRouter()

# Initialize services
document_processor = DocumentProcessor()
task_router = TaskRouter()
orchestrator = TenderOrchestrator(task_router=task_router)


class DocumentProcessResponse(BaseModel):
    """Response model for document processing"""
    success: bool
    filename: str
    file_size: int
    document_type: str
    text_content: str
    pages: int
    extraction_method: str
    metadata: dict


class DocumentAnalysisResponse(BaseModel):
    """Response model for full document analysis with orchestrator"""
    document_info: dict
    orchestrator_result: dict
    success: bool
    message: str


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_document(
    file: UploadFile = File(...),
    case_id: Optional[str] = Form(None),
    auto_process: bool = Form(True)
) -> DocumentAnalysisResponse:
    """
    Upload a document for processing

    This endpoint:
    1. Accepts PDF, images (JPG, PNG), Word, Excel documents
    2. Extracts text content (with OCR for images/scanned PDFs)
    3. Sends extracted text to orchestrator for task detection
    4. Routes to appropriate AI specialists
    5. Returns both document info and AI analysis

    Args:
        file: The uploaded document
        case_id: Optional case ID to associate with this document
        auto_process: Whether to automatically send to orchestrator (default: True)

    Returns:
        Document info and orchestrator analysis results
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )

        # Read file content
        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file provided"
            )

        # Process document to extract text
        print(f"Processing document: {file.filename} ({len(file_content)} bytes)")

        doc_result = await document_processor.process_document(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )

        if not doc_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process document: {doc_result.get('error', 'Unknown error')}"
            )

        # If auto_process is enabled, send to orchestrator
        orchestrator_result = None
        if auto_process and doc_result.get("text_content"):
            print(f"Sending extracted text to orchestrator ({len(doc_result['text_content'])} chars)")

            # Create attachment metadata
            attachment_metadata = {
                "filename": file.filename,
                "file_size": doc_result["file_size"],
                "content_type": file.content_type,
                "document_type": doc_result["document_type"],
                "pages": doc_result["pages"],
                "extraction_method": doc_result["extraction_method"]
            }

            # Process through orchestrator
            orchestrator_result = await orchestrator.process_input(
                raw_text=doc_result["text_content"],
                source_type=SourceType.FAX,  # Documents often come via fax/scan
                case_id=case_id,
                metadata={
                    "source": "document_upload",
                    "original_filename": file.filename
                },
                attachments=[attachment_metadata]
            )

        return {
            "success": True,
            "message": f"Document '{file.filename}' processed successfully",
            "document_info": doc_result,
            "orchestrator_result": orchestrator_result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.post("/batch-upload", status_code=status.HTTP_200_OK)
async def batch_upload_documents(
    files: List[UploadFile] = File(...),
    case_id: Optional[str] = Form(None)
):
    """
    Upload multiple documents at once

    Processes multiple files and aggregates results
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )

    results = []
    errors = []

    for file in files:
        try:
            # Process each file
            file_content = await file.read()

            doc_result = await document_processor.process_document(
                file_content=file_content,
                filename=file.filename,
                content_type=file.content_type
            )

            results.append({
                "filename": file.filename,
                "success": doc_result.get("success", False),
                "text_length": len(doc_result.get("text_content", "")),
                "pages": doc_result.get("pages", 0),
                "extraction_method": doc_result.get("extraction_method", "unknown")
            })

        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })

    # Combine all extracted text and send to orchestrator
    combined_text = "\n\n---\n\n".join([
        f"Document: {r['filename']}\n{results[i].get('text_content', '')}"
        for i, r in enumerate(results)
        if r.get("text_content")
    ])

    orchestrator_result = None
    if combined_text:
        orchestrator_result = await orchestrator.process_input(
            raw_text=combined_text,
            source_type=SourceType.FAX,
            case_id=case_id,
            metadata={
                "source": "batch_upload",
                "file_count": len(files)
            }
        )

    return {
        "success": True,
        "message": f"Processed {len(results)} document(s)",
        "results": results,
        "errors": errors,
        "orchestrator_result": orchestrator_result
    }


@router.get("/supported-types", status_code=status.HTTP_200_OK)
async def get_supported_types():
    """
    Get list of supported document types
    """
    return {
        "supported_types": document_processor.get_supported_types(),
        "ocr_available": document_processor.ocr_available,
        "max_file_size_mb": document_processor.max_file_size / 1024 / 1024
    }


@router.post("/extract-text", status_code=status.HTTP_200_OK)
async def extract_text_only(file: UploadFile = File(...)):
    """
    Extract text from document without sending to orchestrator

    Useful for preview or manual review before processing
    """
    try:
        file_content = await file.read()

        doc_result = await document_processor.process_document(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )

        return doc_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text: {str(e)}"
        )
