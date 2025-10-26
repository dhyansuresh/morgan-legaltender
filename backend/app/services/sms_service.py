"""
SMS Service using Twilio for sending and receiving text messages
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


class SMSService:
    """Service for SMS operations using Twilio"""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.enabled = bool(self.account_sid and self.auth_token and self.from_number)

        if self.enabled:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None

        # In-memory storage for demo (use database in production)
        self.message_history: List[Dict[str, Any]] = []

    async def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        """Send an SMS message"""
        if not self.enabled:
            # Mock response for testing when Twilio is not configured
            mock_response = {
                "sid": f"SM{datetime.utcnow().timestamp()}",
                "status": "sent",
                "to": to,
                "from": self.from_number or "+1234567890",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.message_history.append({
                **mock_response,
                "direction": "outbound"
            })
            return mock_response

        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to
            )

            response = {
                "sid": message_obj.sid,
                "status": message_obj.status,
                "to": message_obj.to,
                "from": message_obj.from_,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Store in history
            self.message_history.append({
                **response,
                "direction": "outbound"
            })

            return response

        except TwilioRestException as e:
            raise Exception(f"Failed to send SMS: {e.msg}")
        except Exception as e:
            raise Exception(f"Unexpected error sending SMS: {str(e)}")

    async def get_message_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get SMS message history"""
        if not self.enabled:
            # Return mock history
            return self.message_history[-limit:] if len(self.message_history) > limit else self.message_history

        try:
            messages = self.client.messages.list(limit=limit)

            history = []
            for msg in messages:
                history.append({
                    "sid": msg.sid,
                    "to": msg.to,
                    "from": msg.from_,
                    "message": msg.body,
                    "status": msg.status,
                    "timestamp": msg.date_sent.isoformat() if msg.date_sent else datetime.utcnow().isoformat(),
                    "direction": msg.direction
                })

            return history

        except TwilioRestException as e:
            raise Exception(f"Failed to get message history: {e.msg}")
        except Exception as e:
            # Return local history as fallback
            return self.message_history[-limit:] if len(self.message_history) > limit else self.message_history

    async def receive_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming SMS webhook from Twilio"""
        # Store incoming message
        incoming_message = {
            "sid": data.get("MessageSid"),
            "from": data.get("From"),
            "to": data.get("To"),
            "message": data.get("Body"),
            "status": "received",
            "timestamp": datetime.utcnow().isoformat(),
            "direction": "inbound"
        }

        self.message_history.append(incoming_message)

        return {
            "status": "received",
            "message": "SMS received and will be processed"
        }


# Singleton instance
sms_service = SMSService()
