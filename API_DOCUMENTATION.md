# Tender for Lawyers - API Documentation

## Overview

The Tender for Lawyers API is an AI-powered internal assistant system for law firms that processes messy, multi-source inputs and routes tasks to specialized AI agents.

**Base URL**: `http://localhost:8000`
**API Documentation**: `http://localhost:8000/docs` (Swagger UI)
**Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

---

## Authentication

Currently, the API does not require authentication for development. In production, implement proper authentication using JWT tokens or API keys.

---

## Main Endpoints

### 1. Orchestrator Endpoints

The main orchestrator processes incoming messages and routes them to appropriate specialists.

#### Process Input

```http
POST /api/orchestrator/process
```

Process incoming messy input (email, SMS, transcript, etc.)

**Request Body:**
```json
{
  "raw_text": "Hi, I had my MRI done at Dr. Smith's office yesterday...",
  "source_type": "email",
  "case_id": "CASE-2024-001",
  "metadata": {
    "sender": "client@example.com",
    "received_at": "2024-01-15T10:30:00Z"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Input processed successfully",
  "data": {
    "processing_id": "PROC-1234567890",
    "case_id": "CASE-2024-001",
    "source_type": "email",
    "normalized_text": "...",
    "extracted_entities": {
      "names": [],
      "dates": ["01/15/2024"],
      "medical_terms": ["MRI", "Dr. Smith"],
      "monetary_amounts": ["$2,500"]
    },
    "pii_phi_labels": {
      "pii": [...],
      "phi": [...]
    },
    "detected_tasks": [
      {
        "id": "TASK-001",
        "task_type": "retrieve_records",
        "priority": "medium",
        "description": "Retrieve medical records from Dr. Smith"
      }
    ],
    "routing_decisions": [
      {
        "agent_id": "records_wrangler",
        "agent_name": "Records Wrangler",
        "confidence": 0.95,
        "reasoning": "..."
      }
    ],
    "approval_required": "pending",
    "proposed_actions": [...]
  }
}
```

#### Process with Attachments

```http
POST /api/orchestrator/process-with-attachments
```

Process input with file attachments.

**Form Data:**
- `raw_text`: String
- `source_type`: String
- `case_id`: String (optional)
- `files`: File[] (optional)

#### Approve Action

```http
POST /api/orchestrator/approve-action
```

Approve or reject a proposed action (HUMAN_APPROVAL gate).

**Request Body:**
```json
{
  "processing_id": "PROC-1234567890",
  "task_id": "TASK-001",
  "approval_status": "approved",
  "reviewer_notes": "Looks good, proceed",
  "modifications": {}
}
```

#### Get Pending Approvals

```http
GET /api/orchestrator/pending-approvals?case_id=CASE-2024-001
```

Get all actions pending human approval.

#### Get Processing History

```http
GET /api/orchestrator/processing-history?case_id=CASE-2024-001&limit=50
```

Get processing history, optionally filtered by case.

---

### 2. AI Specialist Endpoints

Direct endpoints for each AI specialist.

#### Records Wrangler

**Analyze Records Needs**
```http
POST /api/specialists/records-wrangler/analyze
```

**Request:**
```json
{
  "text": "I had an MRI at City Hospital and saw Dr. Johnson. Bill was $3,500.",
  "case_id": "CASE-2024-001",
  "existing_records": ["Initial consultation"]
}
```

**Draft Provider Outreach**
```http
POST /api/specialists/records-wrangler/draft-outreach
```

**Query Parameters:**
- `provider_name`: String
- `record_types`: Array of strings
- `case_id`: String (optional)
- `patient_name`: String (optional)

#### Voice Scheduler

**Parse Scheduling Request**
```http
POST /api/specialists/voice-scheduler/parse-request
```

**Request:**
```json
{
  "text": "We need to schedule the deposition for next Tuesday afternoon.",
  "case_id": "CASE-2024-001"
}
```

**Generate Scheduling Options**
```http
POST /api/specialists/voice-scheduler/generate-options
```

**Query Parameters:**
- `appointment_type`: String
- `duration_minutes`: Integer (default: 60)

**Draft Scheduling Message**
```http
POST /api/specialists/voice-scheduler/draft-message
```

**Query Parameters:**
- `recipient_name`: String
- `appointment_type`: String
- `proposed_slot_ids`: Array of strings
- `case_id`: String (optional)

#### Evidence Sorter

**Analyze Single Document**
```http
POST /api/specialists/evidence-sorter/analyze-document
```

**Request:**
```json
{
  "filename": "medical_records_dr_smith.pdf",
  "text_content": "Patient: John Doe. Date: 01/15/2024...",
  "file_size": 245000,
  "case_id": "CASE-2024-001"
}
```

**Process Document Batch**
```http
POST /api/specialists/evidence-sorter/process-batch
```

**Request:**
```json
{
  "documents": [
    {
      "filename": "doc1.pdf",
      "text_content": "...",
      "file_size": 125000
    }
  ],
  "case_id": "CASE-2024-001"
}
```

**Generate Salesforce Payload**
```http
POST /api/specialists/evidence-sorter/salesforce-payload
```

#### Legal Researcher

**Analyze Legal Issues**
```http
POST /api/specialists/legal-researcher/analyze
```

**Request:**
```json
{
  "text": "Client was rear-ended and suffered whiplash. Other driver was texting.",
  "case_id": "CASE-2024-001",
  "metadata": {}
}
```

#### Client Communication Guru

**Draft Client Communication**
```http
POST /api/specialists/client-communication/draft
```

**Request:**
```json
{
  "client_name": "Jane Doe",
  "purpose": "status update",
  "text": "Client is asking about case progress and next steps."
}
```

---

### 3. Task Router Endpoints

Manage task routing and agent status.

#### Route Single Task

```http
POST /api/router/route
```

**Request:**
```json
{
  "task_id": "TASK-001",
  "task_type": "retrieve_records",
  "priority": "high",
  "description": "Retrieve medical records",
  "extracted_data": {}
}
```

#### Route Multiple Tasks

```http
POST /api/router/route/batch
```

#### Get Agent Status

```http
GET /api/router/agents/status
GET /api/router/agents/{agent_id}/status
```

#### Get Routing Statistics

```http
GET /api/router/stats
```

#### Get Supported Task Types

```http
GET /api/router/task-types
```

---

## Source Types

Supported input source types:

- `email` - Email messages
- `sms` - Text messages
- `client_portal` - Client portal messages
- `phone_transcript` - Phone call transcripts
- `voicemail` - Voicemail transcripts
- `fax` - Faxed documents (OCR processed)
- `manual_entry` - Manually entered notes

---

## Task Types

Detected task types:

- `retrieve_records` - Retrieve medical records/bills
- `client_communication` - Respond to client inquiry
- `legal_research` - Conduct legal research
- `schedule_appointment` - Schedule meetings/depositions
- `document_organization` - Organize documents
- `deadline_reminder` - Set deadline reminders
- `follow_up` - Follow up actions
- `draft_letter` - Draft legal correspondence
- `court_filing` - Prepare court filings

---

## Agent Types

Available AI specialists:

- `records_wrangler` - Records Wrangler
- `communication_guru` - Client Communication Guru
- `legal_researcher` - Legal Researcher
- `voice_scheduler` - Voice Bot Scheduler
- `evidence_sorter` - Evidence Sorter

---

## Priority Levels

Task priority levels:

- `urgent` - Requires immediate attention
- `high` - Important, needs attention soon
- `medium` - Normal priority (default)
- `low` - Can be handled later

---

## Approval Status

- `pending` - Awaiting human approval
- `approved` - Approved by human
- `rejected` - Rejected by human
- `not_required` - No approval needed

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "path": "/api/endpoint",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Default limits (configurable via environment):
- 60 requests per minute
- 1000 requests per hour

---

## Best Practices

1. **Always include case_id** when processing inputs for proper tracking
2. **Use the test endpoint** `/api/orchestrator/test-input` for quick testing
3. **Respect approval workflow** - Never bypass the HUMAN_APPROVAL gate
4. **Include metadata** for better context and auditing
5. **Handle PII/PHI carefully** - The system labels sensitive data, redact before external use

---

## Example Workflows

### Workflow 1: Process Email and Approve Action

```python
import requests

# Step 1: Process email
response = requests.post(
    "http://localhost:8000/api/orchestrator/process",
    json={
        "raw_text": "I need my MRI records from Dr. Smith urgently!",
        "source_type": "email",
        "case_id": "CASE-2024-001"
    }
)

result = response.json()
processing_id = result["data"]["processing_id"]
task_id = result["data"]["detected_tasks"][0]["id"]

# Step 2: Approve the proposed action
approval = requests.post(
    "http://localhost:8000/api/orchestrator/approve-action",
    json={
        "processing_id": processing_id,
        "task_id": task_id,
        "approval_status": "approved",
        "reviewer_notes": "Approved for execution"
    }
)
```

### Workflow 2: Direct Specialist Call

```python
# Call Records Wrangler directly
response = requests.post(
    "http://localhost:8000/api/specialists/records-wrangler/analyze",
    json={
        "text": "Had MRI at City Hospital, saw Dr. Johnson",
        "case_id": "CASE-2024-001",
        "existing_records": []
    }
)

result = response.json()
providers = result["data"]["identified_providers"]
draft_letters = result["data"]["draft_requests"]
```

---

## Support

For API issues or questions:
- GitHub Issues: https://github.com/yourusername/morgan-legaltender/issues
- Email: dhyan.sur@gmail.com

---

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Main orchestrator with PII/PHI detection
- 5 AI specialists implemented
- Human approval workflow
- Task routing system
