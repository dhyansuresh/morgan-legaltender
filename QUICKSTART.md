# 🚀 Quick Start Guide

## You're Already Set Up! ✅

Your API keys are configured and ready to use.

---

## What You Have

✅ **OpenAI API Key** - Configured and ready
✅ **Google AI API Key** - Configured as backup
✅ **Environment file** - Created at `backend/.env`

---

## Start the Server (3 Commands)

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start the server
python app.py
```

**Server will start at**: http://localhost:8000

---

## Access the API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Try It Out!

### Option 1: Use the Browser (Easiest)

1. Go to: http://localhost:8000/docs
2. Find the endpoint: `POST /api/orchestrator/process`
3. Click "Try it out"
4. Paste this example:

```json
{
  "raw_text": "I had my MRI done at Dr. Smith's office yesterday. The bill was $2,500. Can we schedule a meeting to discuss my case?",
  "source_type": "email",
  "case_id": "CASE-2024-001"
}
```

5. Click "Execute"
6. See the AI-powered results! 🎉

### Option 2: Use cURL (Command Line)

```bash
curl -X POST "http://localhost:8000/api/orchestrator/process" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "I need medical records from Dr. Smith. Had MRI last week.",
    "source_type": "email",
    "case_id": "CASE-2024-001"
  }'
```

### Option 3: Use Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/orchestrator/process",
    json={
        "raw_text": "I need medical records from Dr. Smith. Had MRI last week.",
        "source_type": "email",
        "case_id": "CASE-2024-001"
    }
)

print(response.json())
```

---

## What Happens When You Send a Request?

```
Your messy input
      ↓
  Orchestrator
   • Normalizes text
   • Extracts entities (Dr. Smith, $2,500, MRI)
   • Labels PII/PHI
   • Detects tasks (retrieve records, schedule meeting)
      ↓
   Task Router
   • Routes to Records Wrangler
   • Routes to Voice Scheduler
      ↓
  AI Specialists
   • Draft record request letter
   • Suggest meeting times
      ↓
  HUMAN APPROVAL
   • Review proposed actions
   • Approve before sending
```

---

## Expected Response

You'll get back:

```json
{
  "status": "success",
  "data": {
    "detected_tasks": [
      {
        "task_type": "retrieve_records",
        "priority": "medium",
        "description": "Retrieve medical records from Dr. Smith"
      },
      {
        "task_type": "schedule_appointment",
        "priority": "medium"
      }
    ],
    "extracted_entities": {
      "medical_terms": ["MRI", "Dr. Smith"],
      "monetary_amounts": ["$2,500"],
      "dates": ["yesterday"]
    },
    "pii_phi_labels": {
      "phi": [...],
      "pii": [...]
    },
    "routing_decisions": [
      {
        "agent_name": "Records Wrangler",
        "confidence": 0.95
      }
    ],
    "approval_required": "pending",
    "proposed_actions": [...]
  }
}
```

---

## Key Endpoints to Try

### 1. Main Orchestrator
```
POST /api/orchestrator/process
```
Process any messy input (email, SMS, transcript)

### 2. Records Wrangler
```
POST /api/specialists/records-wrangler/analyze
```
Find missing medical records

### 3. Voice Scheduler
```
POST /api/specialists/voice-scheduler/parse-request
```
Parse scheduling requests

### 4. Evidence Sorter
```
POST /api/specialists/evidence-sorter/analyze-document
```
Classify and organize documents

### 5. Legal Researcher
```
POST /api/specialists/legal-researcher/analyze
```
Find legal issues and citations

### 6. Client Communication
```
POST /api/specialists/client-communication/draft
```
Draft empathetic client messages

---

## Test Your Setup

```bash
# Quick test
cd backend
python test_api_key.py

# Should show:
# ✅ SUCCESS! At least one API key is configured.
```

---

## Troubleshooting

### Server won't start?

```bash
# Make sure you're in backend directory
pwd  # Should end with /backend

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
ls -la .env

# Try again
python app.py
```

### API key errors?

```bash
# Test your keys
python test_api_key.py

# Check .env file
cat .env | grep API_KEY
```

### Import errors?

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## Stop the Server

Press `Ctrl + C` in the terminal where the server is running.

---

## Next Steps

1. ✅ Start the server
2. ✅ Visit http://localhost:8000/docs
3. ✅ Try the orchestrator endpoint
4. ✅ Test each specialist
5. ✅ Process a real email or text message
6. ✅ Review the proposed actions

---

## Full Documentation

- **API Reference**: See `API_DOCUMENTATION.md`
- **Deployment Guide**: See `DEPLOYMENT.md`
- **API Keys Setup**: See `SETUP_API_KEYS.md`

---

## Summary

```bash
# Everything you need:
cd backend
source venv/bin/activate
python app.py

# Then visit: http://localhost:8000/docs
```

**That's it! You're ready to go!** 🎉

---

## Support

Questions? Check:
- Swagger UI: http://localhost:8000/docs (when server running)
- API_DOCUMENTATION.md
- SETUP_API_KEYS.md

---

**Built with FastAPI, powered by AI** 🚀
