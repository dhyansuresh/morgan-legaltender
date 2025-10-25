import os
import typing as t
import httpx


class OpenAIAdapter:
    """A minimal async adapter that calls OpenAI's Chat Completions REST API via httpx.

    Usage:
      adapter = OpenAIAdapter(api_key=os.environ.get('OPENAI_API_KEY'))
      await adapter.complete(prompt)

    This keeps the dependency surface small (only httpx required). If you prefer the
    official `openai` package or LangChain, use those instead.
    """

    def __init__(self, api_key: t.Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIAdapter")
        self.model = model
        self._endpoint = "https://api.openai.com/v1/chat/completions"

    async def complete(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful legal research assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 800,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(self._endpoint, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
        # basic extraction of text
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            # fallback to raw json string if structure differs
            return str(data)
