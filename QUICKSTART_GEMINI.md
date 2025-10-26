# Quick Start: Gemini Conversational AI

## Setup (5 minutes)

### 1. Set API Key

Make sure your `.env` file in the `backend/` directory has:

```bash
GOOGLE_AI_API_KEY=your_actual_gemini_api_key_here
```

Get a free API key at: https://makersuite.google.com/app/apikey

### 2. Install Dependencies (if not already done)

```bash
cd backend
pip install -r requirements.txt
```

## Test It Works (2 minutes)

### Option 1: Python Test Script

```bash
cd backend
python test_gemini_conversation.py
```

This runs 6 comprehensive tests showing all conversation modes. You should see:
- ✅ Single-shot completions
- ✅ Multi-turn conversations with context
- ✅ System instruction demonstrations
- ✅ Legal research scenario
- ✅ Client communication scenario

### Option 2: API Endpoint Tests

```bash
# Start the server first
cd backend
python main.py

# In another terminal, run the API tests
./test_gemini_api.sh
```

This tests all the REST API endpoints.

## Quick Examples

### Python: Single Question

```python
from app.specialists.gemini_adapter import GeminiAdapter
import asyncio

async def main():
    adapter = GeminiAdapter()
    response = await adapter.complete("What are the elements of negligence?")
    print(response)

asyncio.run(main())
```

### Python: Conversation

```python
from app.specialists.gemini_adapter import GeminiAdapter
import asyncio

async def main():
    adapter = GeminiAdapter(
        system_instruction="You are a legal research assistant."
    )
    
    # Turn 1
    r1 = await adapter.add_to_conversation("What is negligence?")
    print(f"AI: {r1}\n")
    
    # Turn 2 (has context from turn 1)
    r2 = await adapter.add_to_conversation("Can you give an example?")
    print(f"AI: {r2}\n")
    
    # Turn 3 (has context from turns 1 & 2)
    r3 = await adapter.add_to_conversation("How does this apply to car accidents?")
    print(f"AI: {r3}\n")

asyncio.run(main())
```

### API: Start Conversation

```bash
curl -X POST http://localhost:8000/api/conversation/start \
  -H "Content-Type: application/json" \
  -d '{
    "system_instruction": "You are a legal assistant.",
    "initial_message": "What is negligence?"
  }'
```

### API: Continue Conversation

```bash
curl -X POST http://localhost:8000/api/conversation/continue \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv-1234567890",
    "message": "Can you give an example?"
  }'
```

## Use in Your Specialists

### Legal Researcher

The Legal Researcher already uses Gemini with proper system instructions:

```bash
curl -X POST http://localhost:8000/api/specialists/legal-researcher/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Client was rear-ended. Has whiplash. Other driver was texting.",
    "case_id": "CASE-001"
  }'
```

### Client Communication

The Client Communicator also uses Gemini:

```bash
curl -X POST http://localhost:8000/api/specialists/client-communication/draft \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Smith",
    "purpose": "case update",
    "text": "We sent demand letter. Awaiting response from insurance."
  }'
```

## View API Documentation

```bash
# Start server
cd backend
python main.py

# Open in browser
http://localhost:8000/docs
```

Look for the "Gemini Conversations" section.

## Troubleshooting

### "GOOGLE_AI_API_KEY is required"
- Check your `.env` file
- Make sure the key is valid
- Run: `python backend/test_api_key.py`

### "Server is not running"
```bash
cd backend
python main.py
```

### "Unexpected API response"
- Your API key might be invalid
- Check if you have quota remaining
- Verify the model name is correct

### Context not maintained
- Make sure you're using the same adapter instance
- Don't recreate the adapter for each message
- Use `add_to_conversation()` method

## What's Different Now?

### Before ❌
```python
# Each call was independent, no context
response1 = await adapter.complete("What is negligence?")
response2 = await adapter.complete("Give an example")  # Doesn't know about response1
```

### Now ✅
```python
# Maintains full conversation context
response1 = await adapter.add_to_conversation("What is negligence?")
response2 = await adapter.add_to_conversation("Give an example")  # Knows about response1!
```

## Key Features

1. ✅ **Multi-turn conversations** - Maintains context across messages
2. ✅ **System instructions** - Set AI role and behavior
3. ✅ **Stateful mode** - Server manages conversation history
4. ✅ **Stateless mode** - Client manages conversation history
5. ✅ **Better responses** - Context-aware, role-specific answers
6. ✅ **Easy to use** - Simple Python and REST APIs

## Next Steps

1. ✅ Run `python backend/test_gemini_conversation.py`
2. ✅ Review the outputs
3. ✅ Read `GEMINI_CONVERSATION_GUIDE.md` for details
4. ✅ Customize system instructions for your needs
5. ✅ Integrate with your frontend

## Documentation

- **Complete Guide**: `GEMINI_CONVERSATION_GUIDE.md`
- **Fix Summary**: `GEMINI_FIX_SUMMARY.md`
- **API Docs**: http://localhost:8000/docs

## Get Help

If something isn't working:
1. Run the test script: `python backend/test_gemini_conversation.py`
2. Check the logs in the terminal
3. Review the error message carefully
4. Check your API key is valid

---

**You're all set!** 🎉 

The Gemini integration now supports proper back-and-forth conversations like you'd experience on Google AI Studio.

