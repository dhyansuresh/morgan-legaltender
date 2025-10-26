Backend AI specialist: Legal Researcher

This folder contains a minimal FastAPI service implementing the Legal Researcher AI specialist.

Quick run (development):

1. Create and activate a virtual environment (recommended):

```bash
cd morgan-legaltender/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py
# Or use uvicorn directly:
# python -m uvicorn main:app --reload --port 8000
```

Endpoint:
- POST /ai/legal-research
  - body: { "text": "...messy client email or transcript..." }
  - response: JSON with issues, citations, suggested_actions, brief

Using a real LLM provider
- This service uses a Mock LLM adapter by default. To use an actual OpenAI API key,
  set the `OPENAI_API_KEY` environment variable before starting the server. When
  `OPENAI_API_KEY` is present the app will attempt to use the minimal async
  `OpenAIAdapter` in `app/specialists/openai_adapter.py`.

  Example (PowerShell):

  ```bash
  export OPENAI_API_KEY="sk-..."  # On Windows: $env:OPENAI_API_KEY = "sk-..."
  python main.py
  # Or use uvicorn directly:
  # python -m uvicorn main:app --reload --port 8000
  ```

- The `OpenAIAdapter` calls the OpenAI chat completions endpoint using `httpx`.
  If you prefer the official SDK or LangChain, you can replace the adapter with
  one that wraps `openai` or `langchain`.

LangChain example (optional)
- To use LangChain's async chat models you can implement an adapter like:

```python
from langchain.chat_models import ChatOpenAI

class LangChainAdapter:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model_name=model, openai_api_key=api_key)

    async def complete(self, prompt: str) -> str:
        # LangChain's chat models expose an async API; adapt as needed.
        return await self.llm.agenerate([{"role": "user", "content": prompt}])
```

Install notes
- The adapter file uses `httpx` which is already in `requirements.txt`. To use the
  official OpenAI package or LangChain, install them in your backend venv:

```powershell
python -m pip install openai
# or for LangChain
python -m pip install langchain
```

Security
- Store API keys in environment variables or a secrets manager. Do not commit keys to
  source control.

Extending agents
- The `LegalResearcher` accepts any object implementing `async def complete(prompt: str) -> str`.
  You can build other specialist agents similarly and wire them into a higher-level
  orchestrator.

Client Communication Guru
- Endpoint: POST /ai/client-communication
  - body example:

```json
{
  "client_name": "Jane Doe",
  "purpose": "status update",
  "text": "I was in a car crash last week and had an MRI. The adjuster contacted me."
}
```

  - response: { draft_message, subject, suggested_followups }

This agent drafts clear, empathetic messages for gatekeepers to review before sending to clients.
