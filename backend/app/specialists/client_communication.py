from typing import List, Optional
import re

from ..schemas import CommunicationResponse


class ClientCommAdapter:
    """Adapter interface for a chat/LLM provider. Implement complete(prompt) -> str."""

    async def complete(self, prompt: str) -> str:  # pragma: no cover
        raise NotImplementedError()


class MockCommAdapter(ClientCommAdapter):
    async def complete(self, prompt: str) -> str:
        # Return a polite, empathetic draft for testing.
        return (
            "Hi [Client Name],\n\nThank you for reaching out and I'm sorry to hear about your accident. "
            "We recommend collecting your medical records and we will follow up with next steps.\n\n" 
            "Sincerely,\nYour Legal Team"
        )


class ClientCommunicator:
    """Drafts empathetic, clear client messages from messy context."

    Contract:
    - Input: CommunicationRequest (context text + tone/purpose)
    - Output: CommunicationResponse with draft_message, subject, suggested_followups
    """

    def __init__(self, llm_adapter: Optional[ClientCommAdapter] = None):
        self.llm = llm_adapter or MockCommAdapter()

    def _suggest_subject(self, purpose: Optional[str], text: str) -> str:
        if purpose:
            return f"{purpose.capitalize()} - Update from Your Legal Team"
        # fallback simple subject extraction
        if re.search(r"appointment|schedule|deposition|med(ia|iation)", text, re.I):
            return "Scheduling: Next Steps"
        return "Update from Your Legal Team"

    def _suggest_followups(self, text: str) -> List[str]:
        followups = []
        if re.search(r"mri|x-?ray|surgery|therapy|pt", text, re.I):
            followups.append("Please provide medical records and billing statements.")
        if re.search(r"insurance|adjuster|limits|settle|tender", text, re.I):
            followups.append("Confirm insurance details and policy limits.")
        if not followups:
            followups.append("Confirm any outstanding questions the client may have.")
        return followups

    async def draft(self, client_name: Optional[str], purpose: Optional[str], text: str) -> dict:
        subject = self._suggest_subject(purpose, text)
        suggested_followups = self._suggest_followups(text)

        prompt = (
            f"Draft an empathetic, concise message to a client named {client_name or '[Client Name]'} "
            f"about the following: {text}\nTone: empathetic. Keep it clear and actionable."
        )
        brief = await self.llm.complete(prompt)

        return {
            "draft_message": brief,
            "subject": subject,
            "suggested_followups": suggested_followups,
        }
