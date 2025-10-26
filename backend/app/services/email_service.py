"""
Email Service for handling email forwarding and inbox monitoring
"""
import os
import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from functools import wraps

def sync_to_async(func):
    """Decorator to run sync functions in async context"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper


class EmailService:
    """Service for email operations"""

    def __init__(self):
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.enabled = bool(self.email_address and self.email_password)

    @sync_to_async
    def _connect_imap(self) -> Optional[imaplib.IMAP4_SSL]:
        """Connect to IMAP server"""
        if not self.enabled:
            return None

        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.email_password)
            return mail
        except Exception as e:
            print(f"Failed to connect to IMAP: {e}")
            return None

    @sync_to_async
    def _fetch_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch emails from inbox"""
        emails = []

        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.email_password)
            mail.select("INBOX")

            # Search for all emails
            status, messages = mail.search(None, "ALL")
            if status != "OK":
                return emails

            email_ids = messages[0].split()
            # Get the last N emails
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids

            for email_id in reversed(email_ids):
                try:
                    status, msg_data = mail.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        continue

                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])

                            # Decode subject
                            subject = msg.get("Subject", "")
                            if subject:
                                decoded = decode_header(subject)
                                subject = decoded[0][0]
                                if isinstance(subject, bytes):
                                    subject = subject.decode(decoded[0][1] or 'utf-8')

                            # Get sender
                            from_addr = msg.get("From", "")

                            # Get date
                            date_str = msg.get("Date", "")

                            # Get body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    if content_type == "text/plain":
                                        try:
                                            body = part.get_payload(decode=True).decode()
                                            break
                                        except:
                                            pass
                            else:
                                try:
                                    body = msg.get_payload(decode=True).decode()
                                except:
                                    body = str(msg.get_payload())

                            emails.append({
                                "id": email_id.decode(),
                                "subject": subject,
                                "from": from_addr,
                                "body": body[:500],  # Limit body length
                                "received_at": date_str or datetime.utcnow().isoformat(),
                                "processed": False
                            })

                except Exception as e:
                    print(f"Error processing email {email_id}: {e}")
                    continue

            mail.close()
            mail.logout()

        except Exception as e:
            print(f"Error fetching emails: {e}")

        return emails

    async def get_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get emails from inbox"""
        if not self.enabled:
            return []

        return await self._fetch_emails(limit)

    async def forward_email_to_agent(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process forwarded email and route to appropriate agent"""
        # This would integrate with your task router
        # For now, just return a mock response
        return {
            "status": "received",
            "email_id": email_data.get("id", "unknown"),
            "message": "Email received and will be processed"
        }


# Singleton instance
email_service = EmailService()
