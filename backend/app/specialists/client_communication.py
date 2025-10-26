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

    def __init__(self, llm_adapter=None):
        # Accept any adapter with a complete() method (Gemini, OpenAI, or Mock)
        self.llm = llm_adapter if llm_adapter else MockCommAdapter()
        
        # Set system instruction if using Gemini adapter
        if self.llm and hasattr(self.llm, 'set_system_instruction'):
            self.llm.set_system_instruction(
                "You are an experienced legal assistant specializing in client communications for a personal "
                "injury law firm. Your role is to draft clear, empathetic, and professional messages to clients. "
                "Always maintain a warm but professional tone, avoid legal jargon unless necessary (and explain it "
                "when used), show genuine concern for the client's wellbeing, provide clear next steps, and ensure "
                "all communications comply with legal and ethical standards. Focus on building trust and keeping "
                "clients informed about their case progress."
            )

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

        prompt = f"""You are an experienced legal assistant helping to draft clear, empathetic client communications.

Client Name: {client_name or '[Client Name]'}
Purpose: {purpose or 'general update'}
Context: {text}

Please draft a professional, empathetic email message to this client. The message should:
1. Be warm and compassionate while maintaining professionalism
2. Clearly address their concerns or questions
3. Provide specific next steps or timeline when appropriate
4. Use plain language (avoid excessive legal jargon)
5. Be concise but thorough (2-4 paragraphs)
6. Include an appropriate greeting and closing

Draft the complete email message:"""

        brief = await self.llm.complete(prompt)

        return {
            "draft_message": brief,
            "subject": subject,
            "suggested_followups": suggested_followups,
        }
