"""
Communication endpoints for Email and SMS
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.email_service import email_service
from app.services.sms_service import sms_service


router = APIRouter()


# Request/Response Models
class EmailForwardRequest(BaseModel):
    subject: str = Field(..., description="Email subject")
    from_email: str = Field(..., alias="from", description="Sender email address")
    body: str = Field(..., description="Email body")
    attachments: Optional[List[str]] = Field(default=None, description="List of attachment URLs or IDs")


class SMSRequest(BaseModel):
    to: str = Field(..., description="Recipient phone number (E.164 format)")
    message: str = Field(..., max_length=1600, description="SMS message content")


class SMSWebhookRequest(BaseModel):
    MessageSid: str
    From: str
    To: str
    Body: str


# Email Endpoints
@router.get("/email/inbox", tags=["Email"])
async def get_email_inbox(limit: int = 50):
    """
    Get emails from the configured inbox

    Retrieves the most recent emails from the monitored inbox.
    Requires IMAP credentials to be configured in environment variables.
    """
    try:
        emails = await email_service.get_emails(limit=limit)
        return {
            "status": "success",
            "count": len(emails),
            "emails": emails,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve emails: {str(e)}")


@router.post("/email/forward", tags=["Email"])
async def forward_email(email_data: EmailForwardRequest, background_tasks: BackgroundTasks):
    """
    Process a forwarded email

    Accepts email data and routes it to the appropriate AI agent for processing.
    """
    try:
        result = await email_service.forward_email_to_agent(email_data.model_dump())

        return {
            "status": "success",
            "message": "Email received and queued for processing",
            "email_id": result.get("email_id"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process email: {str(e)}")


# SMS Endpoints
@router.post("/sms/send", tags=["SMS"])
async def send_sms(sms_request: SMSRequest):
    """
    Send an SMS message

    Sends an SMS using Twilio. Requires Twilio credentials to be configured.
    """
    try:
        result = await sms_service.send_sms(
            to=sms_request.to,
            message=sms_request.message
        )

        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sms/history", tags=["SMS"])
async def get_sms_history(limit: int = 50):
    """
    Get SMS message history

    Retrieves sent and received SMS messages.
    """
    try:
        messages = await sms_service.get_message_history(limit=limit)

        return {
            "status": "success",
            "count": len(messages),
            "messages": messages,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve SMS history: {str(e)}")


@router.post("/sms/webhook", tags=["SMS"])
async def sms_webhook(webhook_data: SMSWebhookRequest):
    """
    Twilio SMS webhook endpoint

    Receives incoming SMS messages from Twilio webhook.
    Configure this URL in your Twilio console: https://your-domain.com/api/sms/webhook
    """
    try:
        result = await sms_service.receive_webhook(webhook_data.model_dump())

        # You can add TwiML response here if needed
        return {
            "status": "success",
            "message": result.get("message")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")


@router.get("/communication/status", tags=["Communication"])
async def get_communication_status():
    """
    Get status of communication services

    Returns the availability status of email and SMS services.
    """
    return {
        "email": {
            "enabled": email_service.enabled,
            "configured": bool(email_service.email_address),
            "server": email_service.imap_server
        },
        "sms": {
            "enabled": sms_service.enabled,
            "configured": bool(sms_service.account_sid),
            "from_number": sms_service.from_number
        },
        "timestamp": datetime.utcnow().isoformat()
    }
