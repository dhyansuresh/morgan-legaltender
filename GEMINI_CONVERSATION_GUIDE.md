# Gemini Conversational API Guide

## Overview

The enhanced Gemini adapter now supports true back-and-forth conversations like you'd experience on Google AI Studio. This guide shows you how to use the conversational features.

## What's New

### Enhanced Features
- ✅ **Multi-turn conversations** with context preservation
- ✅ **System instructions** for specialized AI roles
- ✅ **Stateful conversations** (server-managed history)
- ✅ **Stateless conversations** (client-managed history)
- ✅ **Proper role formatting** (user/assistant/model)
- ✅ **Better error handling** and response parsing

## Quick Start

### 1. Test the Conversation Features

```bash
cd backend
python test_gemini_conversation.py
```

This runs comprehensive tests showing all conversation modes.

### 2. Using the API Endpoints

#### Start a Conversation

```bash
curl -X POST http://localhost:8000/api/conversation/start \
  -H "Content-Type: application/json" \
  -d '{
    "system_instruction": "You are a legal research assistant.",
    "initial_message": "What is negligence?"
  }'
```

Response:
```json
{
  "status": "success",
  "conversation_id": "conv-1234567890",
  "response": "Negligence is a legal concept...",
  "message_count": 2
}
```

#### Continue the Conversation

```bash
curl -X POST http://localhost:8000/api/conversation/continue \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv-1234567890",
    "message": "Can you give me an example?"
  }'
```

Response:
```json
{
  "status": "success",
  "conversation_id": "conv-1234567890",
  "response": "For example, if a driver...",
  "message_count": 4
}
```

#### Get Conversation History

```bash
curl http://localhost:8000/api/conversation/conv-1234567890/history
```

#### End Conversation

```bash
curl -X DELETE http://localhost:8000/api/conversation/conv-1234567890
```

### 3. Using in Python Code

#### Single-Shot Completion

```python
from app.specialists.gemini_adapter import GeminiAdapter

adapter = GeminiAdapter()
response = await adapter.complete("What is negligence?")
print(response)
```

#### Stateful Conversation

```python
# Create adapter with system instruction
adapter = GeminiAdapter(
    system_instruction="You are a legal research assistant."
)

# Have a conversation
response1 = await adapter.add_to_conversation("What is negligence?")
response2 = await adapter.add_to_conversation("Give me an example")
response3 = await adapter.add_to_conversation("How does this apply to car accidents?")

# All responses maintain context from previous messages
```

#### Stateless Multi-Turn Chat

```python
adapter = GeminiAdapter()

messages = [
    {"role": "user", "content": "What is negligence?"},
    {"role": "assistant", "content": "Negligence is..."},
    {"role": "user", "content": "Can you give an example?"}
]

response = await adapter.chat(messages)
```

## System Instructions

System instructions dramatically improve response quality by setting the AI's role and behavior.

### Legal Researcher Example

```python
adapter = GeminiAdapter(
    system_instruction="""You are an experienced legal researcher specializing in personal injury law.
    Provide clear, actionable analysis with specific legal principles and case citations when possible."""
)
```

### Client Communication Example

```python
adapter = GeminiAdapter(
    system_instruction="""You are a compassionate legal assistant drafting client communications.
    Use warm, empathetic language. Avoid legal jargon. Keep clients informed and reassured."""
)
```

### Evidence Organizer Example

```python
adapter = GeminiAdapter(
    system_instruction="""You are a document management specialist.
    Categorize legal documents accurately and suggest appropriate filing locations."""
)
```

## API Endpoints

### Conversation Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/conversation/start` | POST | Start a new conversation |
| `/api/conversation/continue` | POST | Continue existing conversation |
| `/api/conversation/{id}/history` | GET | Get conversation history |
| `/api/conversation/{id}` | DELETE | End conversation |
| `/api/conversations/active` | GET | List all active conversations |
| `/api/conversations/clear-all` | POST | Clear all conversations |
| `/api/chat/multi-turn` | POST | Multi-turn chat (stateless) |

### Specialist Endpoints (using Gemini)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/specialists/legal-researcher/analyze` | POST | Legal research with Gemini |
| `/api/specialists/client-communication/draft` | POST | Draft client messages with Gemini |

## Configuration Options

### Temperature

Controls response creativity:
- `0.0-0.3`: Focused, consistent (good for legal analysis)
- `0.4-0.7`: Balanced (good for client communication)
- `0.8-1.0`: Creative (use sparingly for legal content)

```python
adapter = GeminiAdapter(temperature=0.3)
```

### Max Output Tokens

Controls response length:

```python
adapter = GeminiAdapter(max_output_tokens=2048)
```

### Model Selection

Choose different Gemini models:

```python
# Fast, experimental model (default)
adapter = GeminiAdapter(model="gemini-2.0-flash-exp")

# Stable production model
adapter = GeminiAdapter(model="gemini-1.5-pro")

# Flash model for speed
adapter = GeminiAdapter(model="gemini-1.5-flash")
```

## Best Practices

### 1. Use System Instructions

Always set a system instruction for specialized tasks:

```python
# ❌ Bad - Generic responses
adapter = GeminiAdapter()

# ✅ Good - Specialized responses
adapter = GeminiAdapter(
    system_instruction="You are a legal assistant specializing in personal injury cases."
)
```

### 2. Choose the Right Conversation Mode

```python
# Stateful - Good for interactive chat interfaces
adapter = GeminiAdapter(system_instruction="...")
response = await adapter.add_to_conversation(user_message)

# Stateless - Good for API integrations
response = await adapter.chat(message_history)

# Single-shot - Good for one-off questions
response = await adapter.complete(prompt)
```

### 3. Manage Conversation History

```python
# Clear history when context is no longer relevant
adapter.clear_conversation()

# Check history length
if len(adapter.conversation_history) > 20:
    adapter.clear_conversation()
```

### 4. Handle Errors Gracefully

```python
try:
    response = await adapter.complete(prompt)
except ValueError as e:
    # Handle API response format errors
    print(f"API error: {e}")
except Exception as e:
    # Handle other errors
    print(f"Unexpected error: {e}")
```

## Troubleshooting

### "GOOGLE_AI_API_KEY is required"

Make sure you have set the API key in your `.env` file:

```bash
GOOGLE_AI_API_KEY=your_actual_api_key_here
```

### "Unexpected Gemini API response structure"

This usually means:
1. The API key is invalid
2. The model name is incorrect
3. Safety filters blocked the response

Check the error details for more information.

### Conversation not maintaining context

Make sure you're using the same adapter instance:

```python
# ❌ Bad - Creates new adapter each time
def get_response(message):
    adapter = GeminiAdapter()
    return await adapter.add_to_conversation(message)

# ✅ Good - Reuses same adapter
adapter = GeminiAdapter()
async def get_response(message):
    return await adapter.add_to_conversation(message)
```

## Examples

See `test_gemini_conversation.py` for comprehensive examples including:
- Single-shot completions
- Multi-turn conversations
- System instruction impact
- Legal research scenarios
- Client communication scenarios

## Performance Tips

1. **Reuse adapters** - Creating a new adapter for each request is slower
2. **Use appropriate temperature** - Lower = faster, more consistent
3. **Limit conversation history** - Keep last 10-20 messages for best performance
4. **Choose the right model** - Flash models are faster than Pro models

## Support

For issues or questions:
- Check the test script: `python test_gemini_conversation.py`
- Review API docs: http://localhost:8000/docs
- See examples in the code

## Next Steps

1. Run the test script to see all features in action
2. Try the API endpoints with curl or Postman
3. Integrate conversational Gemini into your specialists
4. Customize system instructions for your use case

