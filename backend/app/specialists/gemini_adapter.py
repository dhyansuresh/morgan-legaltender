import os
import typing as t
import httpx
from typing import List, Dict, Any, Optional


class GeminiAdapter:
    """Enhanced async adapter for Google's Gemini API with conversation support.

    This adapter supports:
    - Single-shot completions
    - Multi-turn conversations with history
    - System instructions for better context
    - Proper role-based message formatting

    Usage:
      # Single-shot:
      adapter = GeminiAdapter(api_key=os.environ.get('GOOGLE_AI_API_KEY'))
      response = await adapter.complete(prompt)

      # Conversational:
      adapter = GeminiAdapter(system_instruction="You are a legal assistant.")
      response = await adapter.chat([
          {"role": "user", "content": "What is negligence?"},
          {"role": "assistant", "content": "Negligence is..."},
          {"role": "user", "content": "Can you give an example?"}
      ])
    """

    def __init__(
        self, 
        api_key: t.Optional[str] = None, 
        model: str = "gemini-2.0-flash-exp",
        system_instruction: t.Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: int = 2048
    ):
        self.api_key = api_key or os.environ.get("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY is required for GeminiAdapter")
        self.model = model
        self.system_instruction = system_instruction
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self._endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        # Conversation history for stateful mode
        self.conversation_history: List[Dict[str, Any]] = []

    async def complete(self, prompt: str, system_instruction: t.Optional[str] = None) -> str:
        """
        Call Gemini API to complete a single prompt (stateless).

        Args:
            prompt: The prompt text to send to Gemini
            system_instruction: Optional system instruction to override default

        Returns:
            The generated text response
        """
        params = {"key": self.api_key}

        # Build the payload with proper structure
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": self.temperature,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": self.max_output_tokens,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }

        # Add system instruction if provided
        system_inst = system_instruction or self.system_instruction
        if system_inst:
            payload["systemInstruction"] = {
                "parts": [{
                    "text": system_inst
                }]
            }

        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(self._endpoint, params=params, json=payload)
            r.raise_for_status()
            data = r.json()

        # Extract text from Gemini response
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            # Fallback if structure differs
            raise ValueError(f"Unexpected Gemini API response structure: {data}")

    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        system_instruction: t.Optional[str] = None
    ) -> str:
        """
        Have a multi-turn conversation with Gemini, maintaining context.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Role can be 'user' or 'assistant'
            system_instruction: Optional system instruction to set context

        Returns:
            The assistant's response text

        Example:
            response = await adapter.chat([
                {"role": "user", "content": "What is negligence?"},
                {"role": "assistant", "content": "Negligence is a failure to exercise care."},
                {"role": "user", "content": "Give me an example"}
            ])
        """
        params = {"key": self.api_key}

        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Gemini uses "model" instead of "assistant"
            gemini_role = "model" if role == "assistant" else "user"
            
            contents.append({
                "role": gemini_role,
                "parts": [{
                    "text": content
                }]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": self.max_output_tokens,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }

        # Add system instruction if provided
        system_inst = system_instruction or self.system_instruction
        if system_inst:
            payload["systemInstruction"] = {
                "parts": [{
                    "text": system_inst
                }]
            }

        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(self._endpoint, params=params, json=payload)
            r.raise_for_status()
            data = r.json()

        # Extract text from Gemini response
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError):
            raise ValueError(f"Unexpected Gemini API response structure: {data}")

    async def add_to_conversation(self, user_message: str) -> str:
        """
        Add a message to the ongoing conversation and get a response (stateful).
        
        This maintains conversation history within the adapter instance.

        Args:
            user_message: The user's message to add to the conversation

        Returns:
            The assistant's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Get response using chat method
        response = await self.chat(self.conversation_history, self.system_instruction)

        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def set_system_instruction(self, instruction: str):
        """Set or update the system instruction."""
        self.system_instruction = instruction
