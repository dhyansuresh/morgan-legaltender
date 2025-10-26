# Tender for Lawyers

**AI-Powered Internal Assistant for Law Firms**

An intelligent orchestration system that processes messy, multi-source inputs (emails, SMS, transcripts) and routes tasks to specialized AI agents for legal case management.

---

## Overview

Tender for Lawyers is an internal AI orchestrator designed for plaintiff-side law firms. It acts as a rigorous case-team triage unit that:

- **Normalizes messy text** from emails, SMS, client portals, and call transcripts
- **Extracts structured facts** including medical terms, dates, legal issues, and contact information
- **Detects actionable tasks** such as record retrieval, scheduling, and client communication
- **Routes tasks intelligently** to the most appropriate AI specialist agent
- **Enforces human approval** for all external communications and critical actions
- **Labels PII/PHI** to ensure data protection and compliance

---

## Key Features

✅ **Multi-Source Input Processing**: Handle emails, SMS, transcripts, and more
✅ **5 Specialized AI Agents**: Each expert in their domain
✅ **Intelligent Task Routing**: Load-balanced routing with confidence scoring
✅ **Human-in-the-Loop**: HUMAN_APPROVAL gate prevents autonomous external actions
✅ **PII/PHI Detection**: Automatic identification and labeling of sensitive data
✅ **Entity Extraction**: Names, dates, medical terms, legal issues, monetary amounts
✅ **RESTful API**: Comprehensive FastAPI-based backend
✅ **Comprehensive Testing**: Full test coverage with pytest

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│          Messy Inputs (Email, SMS, Calls)           │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│            Tender Orchestrator                      │
│  • Normalize text                                   │
│  • Extract entities                                 │
│  • Label PII/PHI                                    │
│  • Detect tasks                                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│            Task Router                              │
│  • Intelligent routing                              │
│  • Load balancing                                   │
│  • Priority handling                                │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌─────────────┐ ┌────────────┐ ┌────────────┐
│ Records     │ │ Legal      │ │ Client     │
│ Wrangler    │ │ Researcher │ │ Comm Guru  │
└─────────────┘ └────────────┘ └────────────┘
        │              │              │
        ▼              ▼              ▼
┌─────────────┐ ┌────────────┐
│ Voice       │ │ Evidence   │
│ Scheduler   │ │ Sorter     │
└─────────────┘ └────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│          HUMAN APPROVAL GATE                        │
└─────────────────────────────────────────────────────┘
```

---

## AI Specialist Agents

### 1. Records Wrangler
Pulls missing bills and records from client messages, drafts HIPAA-compliant request letters, and tracks record status.

**Capabilities:**
- Identify medical providers from text
- Detect missing records
- Draft provider outreach letters
- Track billing items

### 2. Client Communication Guru
Drafts clear, empathetic messages for clients based on context and purpose.

**Capabilities:**
- Draft client messages
- Generate appropriate subject lines
- Suggest follow-up actions
- Maintain empathetic, professional tone

### 3. Legal Researcher
Finds supporting verdicts, citations, and legal theories to strengthen cases.

**Capabilities:**
- Identify legal issues
- Find relevant case law
- Suggest legal strategies
- Draft research briefs

### 4. Voice Bot Scheduler
Coordinates depositions, mediations, and client check-ins.

**Capabilities:**
- Parse scheduling requests
- Generate available time slots
- Draft scheduling messages
- Create appointment confirmations

### 5. Evidence Sorter
Extracts and labels attachments from emails, organizes for case management systems.

**Capabilities:**
- Classify documents automatically
- Extract metadata
- Detect duplicates
- Generate Salesforce-compatible payloads

---

## Quick Start

### Prerequisites
- Python 3.12+
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/morgan-legaltender.git
cd morgan-legaltender/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your API keys

# Run the server
python app.py
```

The API will be available at http://localhost:8000

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Usage Examples

### Process an Email

```python
import requests

response = requests.post(
    "http://localhost:8000/api/orchestrator/process",
    json={
        "raw_text": "I had my MRI at Dr. Smith's office yesterday. The bill was $2,500. Can we discuss?",
        "source_type": "email",
        "case_id": "CASE-2024-001"
    }
)

result = response.json()
print(f"Detected {len(result['data']['detected_tasks'])} tasks")
print(f"Approval required: {result['data']['approval_required']}")
```

### Direct Specialist Call

```python
# Call Records Wrangler directly
response = requests.post(
    "http://localhost:8000/api/specialists/records-wrangler/analyze",
    json={
        "text": "Had MRI at City Hospital, saw Dr. Johnson",
        "case_id": "CASE-2024-001"
    }
)

result = response.json()
providers = result["data"]["identified_providers"]
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_orchestrator.py -v
```

See [TESTING.md](TESTING.md) for more details.

---

## Documentation

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [Testing Guide](TESTING.md) - How to run and write tests

---

## Project Structure

```
morgan-legaltender/
├── backend/
│   ├── api/
│   │   └── routers/
│   │       ├── orchestrator_endpoints.py  # Main orchestrator API
│   │       ├── specialist_endpoints.py    # Direct specialist APIs
│   │       └── router_endpoints.py        # Task routing APIs
│   ├── app/
│   │   ├── specialists/
│   │   │   ├── records_wrangler.py
│   │   │   ├── client_communication.py
│   │   │   ├── legal_researcher.py
│   │   │   ├── voice_scheduler.py
│   │   │   └── evidence_sorter.py
│   │   ├── main.py
│   │   └── schemas.py
│   ├── orchestrator/
│   │   ├── tender_orchestrator.py         # Main orchestrator
│   │   └── advanced_router.py             # Task router
│   ├── tests/
│   │   ├── test_orchestrator.py
│   │   ├── test_specialists.py
│   │   ├── test_router.py
│   │   ├── test_legal_researcher.py
│   │   └── test_client_communication.py
│   ├── app.py                             # Main FastAPI application
│   ├── requirements.txt
│   └── pytest.ini
├── .env.example
├── README.md
├── API_DOCUMENTATION.md
├── DEPLOYMENT.md
└── TESTING.md
```

---

## Technology Stack

- **Backend Framework**: FastAPI 0.104.1
- **AI/ML**: OpenAI, Anthropic Claude, Google Gemini, LangChain
- **NLP**: spaCy, NLTK, sentence-transformers
- **Database**: SQLAlchemy, PostgreSQL, Alembic
- **Caching**: Redis, Celery
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: black, flake8, pylint, mypy

---

## Security & Compliance

- **PII/PHI Detection**: Automatic identification of sensitive data
- **HIPAA Compliance**: Designed for healthcare data handling
- **Human Approval**: Required for all external communications
- **Environment Variables**: Secrets never committed to source control
- **Input Validation**: Pydantic models for all API inputs

---

## Contributing

This is a challenge project for KnightHacks / Morgan & Morgan.

For questions or contributions, please open an issue or pull request.

---

## License

MIT License

---

## Contact

- **Developer**: Dhyan Suresh
- **Email**: dhyan.sur@gmail.com
- **GitHub**: https://github.com/dhyansuresh/morgan-legaltender

---

## Acknowledgments

- Built for the Morgan & Morgan KnightHacks Challenge
- Inspired by real-world law firm operational needs
- Designed with human oversight and approval as core principles

---

**Built with FastAPI, powered by AI, designed for legal professionals**
