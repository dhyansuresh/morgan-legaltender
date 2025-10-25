from fastapi import FastAPI

from .schemas import ResearchRequest, ResearchResponse
from .specialists.legal_researcher import LegalResearcher
from .schemas import CommunicationRequest, CommunicationResponse
from .specialists.client_communication import ClientCommunicator

app = FastAPI(title="Tender-for-Lawyers - Legal Researcher Agent")

import os
from dotenv import load_dotenv

# Load environment variables from a .env file (backend/.env) when present.
load_dotenv()

# If an OPENAI_API_KEY is set, try to use the OpenAIAdapter. Otherwise fall back
# to the built-in MockLLMAdapter inside LegalResearcher.
_adapter = None
try:
    if os.environ.get("OPENAI_API_KEY"):
        from .specialists.openai_adapter import OpenAIAdapter

        _adapter = OpenAIAdapter()
except Exception:
    # If adapter import or instantiation fails, continue with the mock adapter.
    _adapter = None

researcher = LegalResearcher(llm_adapter=_adapter)
comm_agent = ClientCommunicator(llm_adapter=_adapter)

@app.post("/ai/legal-research", response_model=ResearchResponse)
async def legal_research_endpoint(req: ResearchRequest):
    """Accept messy input and return legal research suggestions.

    This endpoint is intentionally simple: it returns structured findings and a short brief.
    Humans remain responsible for final decisions.
    """
    out = await researcher.analyze(req.text, metadata=req.metadata or {})
    return out


@app.post("/ai/client-communication", response_model=CommunicationResponse)
async def client_communication_endpoint(req: CommunicationRequest):
    """Draft a clear, empathetic message to a client based on context and purpose."""
    out = await comm_agent.draft(req.client_name, req.purpose, req.text)
    return out
