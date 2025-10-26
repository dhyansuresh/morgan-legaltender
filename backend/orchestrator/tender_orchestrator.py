"""
Tender for Lawyers - Main Orchestrator

This is the core AI Orchestrator that:
1. Normalizes messy, multi-source inputs (emails, SMS, transcripts)
2. Extracts structured facts and entities
3. Detects actionable tasks
4. Routes tasks to appropriate AI specialists
5. Requires HUMAN_APPROVAL before external actions
6. Labels PII/PHI for data protection
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import re
import os

from .advanced_router import TaskRouter, TaskType, AgentType


class SourceType(str, Enum):
    """Types of input sources"""
    EMAIL = "email"
    SMS = "sms"
    CLIENT_PORTAL = "client_portal"
    PHONE_TRANSCRIPT = "phone_transcript"
    VOICEMAIL = "voicemail"
    FAX = "fax"
    MANUAL_ENTRY = "manual_entry"


class ApprovalStatus(str, Enum):
    """Status of human approval"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NOT_REQUIRED = "not_required"


class TenderOrchestrator:
    """
    Main orchestrator for the Tender for Lawyers system.

    Operates as a rigorous case-team triage unit:
    - Reads messy multi-source inputs
    - Extracts structured facts
    - Detects actionable tasks
    - Proposes AI-assisted draft outputs
    - Routes to correct specialists
    - Enforces HUMAN_APPROVAL gate
    """

    def __init__(self, task_router: Optional[TaskRouter] = None):
        """
        Initialize the orchestrator

        Args:
            task_router: Task router instance (creates new if not provided)
        """
        self.task_router = task_router or TaskRouter()
        self.processing_history = []

        # Initialize specialists with Gemini
        self._initialize_specialists()

    def _initialize_specialists(self):
        """Initialize AI specialists with Gemini adapter"""
        from app.specialists.gemini_adapter import GeminiAdapter
        from app.specialists.legal_researcher import LegalResearcher
        from app.specialists.client_communication import ClientCommunicator
        from app.specialists.records_wrangler import RecordsWrangler
        from app.specialists.voice_scheduler import VoiceScheduler
        from app.specialists.evidence_sorter import EvidenceSorter

        # Get Gemini API key
        google_api_key = os.getenv("GOOGLE_AI_API_KEY")

        # Initialize Gemini adapter
        llm_adapter = None
        if google_api_key:
            llm_adapter = GeminiAdapter(api_key=google_api_key)
            print("✓ Orchestrator initialized with Gemini")
        else:
            print("⚠ No GOOGLE_AI_API_KEY found - specialists will use mock responses")

        # Initialize specialists
        self.legal_researcher = LegalResearcher(llm_adapter=llm_adapter)
        self.client_communicator = ClientCommunicator(llm_adapter=llm_adapter)
        self.records_wrangler = RecordsWrangler()
        self.voice_scheduler = VoiceScheduler()
        self.evidence_sorter = EvidenceSorter()

    async def process_input(
        self,
        raw_text: str,
        source_type: SourceType,
        metadata: Optional[Dict[str, Any]] = None,
        case_id: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process incoming messy input and produce structured output

        Args:
            raw_text: Raw text from email, SMS, transcript, etc.
            source_type: Type of input source
            metadata: Additional metadata (sender, timestamp, etc.)
            case_id: Associated case ID if known
            attachments: List of attachment metadata

        Returns:
            Dictionary containing:
                - normalized_text: Cleaned and normalized text
                - extracted_entities: Names, dates, medical terms, etc.
                - detected_tasks: List of actionable tasks
                - pii_labels: Identified PII/PHI
                - routing_decisions: Task routing assignments
                - approval_required: Whether human approval is needed
                - proposed_actions: Draft outputs for human review
        """
        metadata = metadata or {}
        attachments = attachments or []

        # Step 1: Normalize the messy input
        normalized = self._normalize_text(raw_text, source_type)

        # Step 2: Extract entities and structured data
        entities = self._extract_entities(normalized, source_type)

        # Step 3: Detect and label PII/PHI
        pii_labels = self._label_pii_phi(normalized, entities)

        # Step 4: Detect actionable tasks
        detected_tasks = self._detect_tasks(normalized, entities, source_type)

        # Step 5: Route tasks to specialists
        routing_decisions = []
        for task in detected_tasks:
            routing = await self.task_router.route_task(task)
            routing_decisions.append(routing)

        # Step 6: Execute specialists and get AI responses
        specialist_responses = await self._execute_specialists(
            detected_tasks,
            routing_decisions,
            normalized,
            entities
        )

        # Step 7: Determine if human approval is required
        approval_status = self._determine_approval_requirement(
            detected_tasks,
            routing_decisions
        )

        # Step 8: Generate proposed actions/artifacts
        proposed_actions = self._generate_proposed_actions(
            detected_tasks,
            routing_decisions,
            entities,
            specialist_responses
        )

        # Build comprehensive response
        response = {
            "processing_id": f"PROC-{datetime.utcnow().timestamp()}",
            "case_id": case_id,
            "source_type": source_type.value,
            "processed_at": datetime.utcnow().isoformat(),
            "input_summary": {
                "raw_length": len(raw_text),
                "normalized_length": len(normalized),
                "has_attachments": len(attachments) > 0,
                "attachment_count": len(attachments)
            },
            "normalized_text": normalized,
            "extracted_entities": entities,
            "pii_phi_labels": pii_labels,
            "detected_tasks": detected_tasks,
            "routing_decisions": routing_decisions,
            "specialist_responses": specialist_responses,
            "approval_required": approval_status,
            "proposed_actions": proposed_actions,
            "metadata": metadata,
            "attachments": attachments
        }

        # Record in history
        self._record_processing(response)

        return response

    async def _execute_specialists(
        self,
        tasks: List[Dict[str, Any]],
        routing_decisions: List[Dict[str, Any]],
        text: str,
        entities: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Execute the appropriate specialists and get AI-generated responses

        Args:
            tasks: Detected tasks
            routing_decisions: Routing decisions for each task
            text: Normalized text
            entities: Extracted entities

        Returns:
            List of specialist responses with AI-generated content
        """
        specialist_responses = []

        for task, routing in zip(tasks, routing_decisions):
            task_type = task.get("task_type")
            agent_id = routing.get("agent_id")

            try:
                response = None

                # Call the appropriate specialist based on agent_id
                if agent_id == AgentType.LEGAL_RESEARCHER.value:
                    response = await self.legal_researcher.analyze(
                        text=text,
                        metadata=task.get("extracted_data", {})
                    )

                elif agent_id == AgentType.COMMUNICATION_GURU.value:
                    # Extract client name if available
                    client_name = entities.get("names", [None])[0] if entities.get("names") else None
                    response = await self.client_communicator.draft(
                        client_name=client_name,
                        purpose=task_type,
                        text=text
                    )

                elif agent_id == AgentType.RECORDS_WRANGLER.value:
                    response = await self.records_wrangler.analyze_records_needs(
                        text=text,
                        case_id=None,
                        existing_records=[]
                    )

                elif agent_id == AgentType.VOICE_SCHEDULER.value:
                    response = await self.voice_scheduler.parse_scheduling_request(
                        text=text,
                        case_id=None
                    )

                elif agent_id == AgentType.EVIDENCE_SORTER.value:
                    # Evidence sorter typically processes documents
                    # For now, return a placeholder
                    response = {
                        "message": "Evidence Sorter requires document attachments to process"
                    }

                specialist_responses.append({
                    "task_id": task.get("id"),
                    "agent_id": agent_id,
                    "agent_name": routing.get("agent_name"),
                    "response": response,
                    "status": "success"
                })

            except Exception as e:
                specialist_responses.append({
                    "task_id": task.get("id"),
                    "agent_id": agent_id,
                    "agent_name": routing.get("agent_name"),
                    "response": None,
                    "status": "error",
                    "error": str(e)
                })

        return specialist_responses

    def _normalize_text(self, text: str, source_type: SourceType) -> str:
        """
        Normalize messy text input

        - Remove excessive whitespace
        - Fix common formatting issues
        - Preserve paragraph structure
        - Handle source-specific quirks
        """
        # Remove excessive whitespace
        normalized = re.sub(r'\s+', ' ', text.strip())

        # Restore paragraph breaks (preserve double newlines)
        normalized = re.sub(r'\n\s*\n', '\n\n', normalized)

        # Handle email-specific cleanup
        if source_type == SourceType.EMAIL:
            # Remove email headers if present
            normalized = re.sub(r'^(From|To|Subject|Date):.*?\n', '', normalized, flags=re.MULTILINE)
            # Remove reply markers
            normalized = re.sub(r'On .* wrote:', '', normalized)
            normalized = re.sub(r'>+\s*', '', normalized)

        # Handle SMS-specific cleanup
        elif source_type == SourceType.SMS:
            # SMS often has truncated words, preserve as-is but clean whitespace
            pass

        # Handle transcript-specific cleanup
        elif source_type == SourceType.PHONE_TRANSCRIPT:
            # Remove speaker labels if present
            normalized = re.sub(r'^\[?\w+\s*\d*\]?:\s*', '', normalized, flags=re.MULTILINE)
            # Remove timestamp markers
            normalized = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', normalized)

        return normalized.strip()

    def _extract_entities(self, text: str, source_type: SourceType) -> Dict[str, List[str]]:
        """
        Extract key entities from text

        Entities include:
        - Names (people, organizations)
        - Dates and times
        - Medical terms
        - Legal terms
        - Locations
        - Phone numbers, emails
        - Case/claim numbers
        """
        entities = {
            "names": [],
            "dates": [],
            "medical_terms": [],
            "legal_terms": [],
            "locations": [],
            "contact_info": [],
            "case_numbers": [],
            "monetary_amounts": []
        }

        # Extract dates (various formats)
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
        ]
        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            entities["dates"].extend(dates)

        # Extract medical terms
        medical_keywords = [
            r'\b(?:MRI|CT scan|X-ray|ultrasound|surgery|prescription|therapy|PT|physical therapy)\b',
            r'\b(?:Dr\.|Doctor|physician|surgeon|specialist|hospital|clinic|ER|emergency room)\b',
            r'\b(?:injury|fracture|broken|sprain|strain|concussion|whiplash|herniated|disc)\b',
            r'\b(?:pain|swelling|bruising|numbness|headache|dizziness)\b'
        ]
        for pattern in medical_keywords:
            terms = re.findall(pattern, text, re.IGNORECASE)
            entities["medical_terms"].extend(terms)

        # Extract legal terms
        legal_keywords = [
            r'\b(?:negligence|liability|damages|settlement|lawsuit|claim|deposition|mediation)\b',
            r'\b(?:attorney|lawyer|counsel|court|judge|hearing|trial)\b',
            r'\b(?:plaintiff|defendant|insurance|adjuster|policy|coverage)\b'
        ]
        for pattern in legal_keywords:
            terms = re.findall(pattern, text, re.IGNORECASE)
            entities["legal_terms"].extend(terms)

        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        entities["contact_info"].extend([f"phone:{p}" for p in phones])

        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        entities["contact_info"].extend([f"email:{e}" for e in emails])

        # Extract case/claim numbers
        case_pattern = r'\b(?:case|claim|file)\s*(?:#|number|no\.?)?:?\s*([A-Z0-9-]+)\b'
        cases = re.findall(case_pattern, text, re.IGNORECASE)
        entities["case_numbers"].extend(cases)

        # Extract monetary amounts
        money_pattern = r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        amounts = re.findall(money_pattern, text)
        entities["monetary_amounts"].extend(amounts)

        # Remove duplicates from each category
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

    def _label_pii_phi(
        self,
        text: str,
        entities: Dict[str, List[str]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify and label PII (Personally Identifiable Information) and
        PHI (Protected Health Information)

        Returns labeled instances with context
        """
        pii_phi = {
            "pii": [],
            "phi": [],
            "sensitive_locations": []
        }

        # Phone numbers and emails are PII
        for contact in entities.get("contact_info", []):
            pii_phi["pii"].append({
                "type": "contact_info",
                "value": contact,
                "requires_protection": True
            })

        # Medical terms indicate PHI
        for term in entities.get("medical_terms", []):
            pii_phi["phi"].append({
                "type": "medical_information",
                "term": term,
                "requires_hipaa_protection": True
            })

        # SSN pattern (if present)
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        ssns = re.findall(ssn_pattern, text)
        for ssn in ssns:
            pii_phi["pii"].append({
                "type": "ssn",
                "value": "***-**-****",  # Masked
                "requires_protection": True,
                "severity": "critical"
            })

        # Mark sensitive data locations in text for redaction
        sensitive_patterns = {
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        }

        for label, pattern in sensitive_patterns.items():
            for match in re.finditer(pattern, text):
                pii_phi["sensitive_locations"].append({
                    "type": label,
                    "start": match.start(),
                    "end": match.end(),
                    "should_redact": True
                })

        return pii_phi

    def _detect_tasks(
        self,
        text: str,
        entities: Dict[str, List[str]],
        source_type: SourceType
    ) -> List[Dict[str, Any]]:
        """
        Detect actionable tasks from the normalized text

        Tasks might include:
        - Retrieve medical records
        - Schedule appointments
        - Respond to adjuster
        - Draft demand letter
        - Request missing documents
        - Follow up with client
        """
        tasks = []
        task_id_counter = int(datetime.utcnow().timestamp() * 1000)

        # Task detection patterns
        task_patterns = {
            TaskType.RETRIEVE_RECORDS: [
                r'\b(?:need|get|obtain|request|retrieve)\s+(?:medical\s+)?(?:records|bills|receipts|documents)\b',
                r'\b(?:missing|don\'t have)\s+(?:my|the)?\s*(?:records|bills|documents)\b',
                r'\bmedical\s+(?:records|bills|documentation)\b'
            ],
            TaskType.SCHEDULE_APPOINTMENT: [
                r'\b(?:schedule|book|set up|arrange)\s+(?:an?\s+)?(?:appointment|meeting|deposition|mediation)\b',
                r'\bneed\s+to\s+(?:see|meet|speak with)\b',
                r'\bwhen\s+can\s+(?:we|I)\s+meet\b'
            ],
            TaskType.CLIENT_COMMUNICATION: [
                r'\b(?:update|let me know|inform|tell|status|what\'s happening)\b',
                r'\b(?:question|confused|wondering|clarify)\b',
                r'\bhow\s+is\s+(?:my|the)\s+case\b'
            ],
            TaskType.LEGAL_RESEARCH: [
                r'\b(?:precedent|case law|similar cases|statute|regulation)\b',
                r'\b(?:liability|negligence|duty|breach)\b',
                r'\blegal\s+(?:basis|theory|argument)\b'
            ],
            TaskType.DRAFT_LETTER: [
                r'\b(?:demand|settlement|offer|proposal)\s+letter\b',
                r'\b(?:draft|prepare|write)\s+(?:a\s+)?(?:letter|response|reply)\b'
            ],
            TaskType.DOCUMENT_ORGANIZATION: [
                r'\b(?:organize|sort|file|categorize)\s+(?:documents|files|attachments)\b',
                r'\battachment|attached|enclosed\b'
            ]
        }

        # Detect tasks based on patterns
        for task_type, patterns in task_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Determine priority based on urgency indicators
                    priority = self._determine_priority(text)

                    # Extract relevant context
                    context = self._extract_task_context(text, task_type, entities)

                    task = {
                        "id": f"TASK-{task_id_counter}",
                        "task_type": task_type.value,
                        "priority": priority,
                        "description": self._generate_task_description(task_type, context),
                        "extracted_data": context,
                        "detected_at": datetime.utcnow().isoformat(),
                        "source_type": source_type.value
                    }

                    tasks.append(task)
                    task_id_counter += 1
                    break  # Only create one task per type

        return tasks

    def _determine_priority(self, text: str) -> str:
        """Determine task priority based on urgency indicators"""
        urgent_keywords = [
            r'\b(?:urgent|asap|emergency|immediately|critical|deadline)\b',
            r'\b(?:today|right away|soon as possible)\b'
        ]

        high_keywords = [
            r'\b(?:important|priority|quickly|fast)\b',
            r'\b(?:this week|by friday)\b'
        ]

        for pattern in urgent_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                return "urgent"

        for pattern in high_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                return "high"

        return "medium"

    def _extract_task_context(
        self,
        text: str,
        task_type: TaskType,
        entities: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Extract relevant context for a specific task type"""
        context = {}

        if task_type == TaskType.RETRIEVE_RECORDS:
            context["medical_terms"] = entities.get("medical_terms", [])
            context["providers"] = self._extract_providers(text)

        elif task_type == TaskType.SCHEDULE_APPOINTMENT:
            context["dates"] = entities.get("dates", [])
            context["appointment_type"] = self._extract_appointment_type(text)

        elif task_type == TaskType.CLIENT_COMMUNICATION:
            context["questions"] = self._extract_questions(text)
            context["concerns"] = self._extract_concerns(text)

        elif task_type == TaskType.LEGAL_RESEARCH:
            context["legal_terms"] = entities.get("legal_terms", [])
            context["research_topics"] = self._extract_research_topics(text)

        return context

    def _extract_providers(self, text: str) -> List[str]:
        """Extract medical provider names"""
        provider_pattern = r'\b(?:Dr\.|Doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        providers = re.findall(provider_pattern, text)

        # Also look for hospital/clinic names
        facility_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Hospital|Clinic|Medical Center|Health)\b'
        facilities = re.findall(facility_pattern, text)

        return list(set(providers + facilities))

    def _extract_appointment_type(self, text: str) -> Optional[str]:
        """Extract type of appointment"""
        if re.search(r'\bdeposition\b', text, re.IGNORECASE):
            return "deposition"
        elif re.search(r'\bmediation\b', text, re.IGNORECASE):
            return "mediation"
        elif re.search(r'\bconsultation\b', text, re.IGNORECASE):
            return "consultation"
        return "general_meeting"

    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions from text"""
        # Simple question extraction
        question_pattern = r'([^.!?]*\?)'
        questions = re.findall(question_pattern, text)
        return [q.strip() for q in questions if len(q.strip()) > 10]

    def _extract_concerns(self, text: str) -> List[str]:
        """Extract client concerns"""
        concern_keywords = [
            "worried", "concerned", "confused", "upset",
            "don't understand", "not sure", "wondering"
        ]
        concerns = []
        for keyword in concern_keywords:
            if keyword in text.lower():
                concerns.append(f"Client expressed: {keyword}")
        return concerns

    def _extract_research_topics(self, text: str) -> List[str]:
        """Extract legal research topics"""
        topics = []
        legal_areas = {
            "negligence": "Negligence law",
            "liability": "Liability analysis",
            "damages": "Damages calculation",
            "comparative": "Comparative negligence",
            "statute of limitations": "Statute of limitations"
        }

        for keyword, topic in legal_areas.items():
            if keyword in text.lower():
                topics.append(topic)

        return topics

    def _generate_task_description(
        self,
        task_type: TaskType,
        context: Dict[str, Any]
    ) -> str:
        """Generate a human-readable task description"""
        descriptions = {
            TaskType.RETRIEVE_RECORDS: f"Retrieve medical records and bills",
            TaskType.SCHEDULE_APPOINTMENT: f"Schedule {context.get('appointment_type', 'appointment')}",
            TaskType.CLIENT_COMMUNICATION: "Respond to client inquiry",
            TaskType.LEGAL_RESEARCH: "Conduct legal research",
            TaskType.DRAFT_LETTER: "Draft legal correspondence",
            TaskType.DOCUMENT_ORGANIZATION: "Organize and file documents"
        }

        base_description = descriptions.get(task_type, "Process task")

        # Add context details
        if task_type == TaskType.RETRIEVE_RECORDS and context.get("providers"):
            providers = ", ".join(context["providers"][:2])
            base_description += f" from {providers}"

        return base_description

    def _determine_approval_requirement(
        self,
        tasks: List[Dict[str, Any]],
        routing_decisions: List[Dict[str, Any]]
    ) -> ApprovalStatus:
        """
        Determine if human approval is required

        Rules:
        - All external communications require approval
        - High-value decisions require approval
        - Routine record requests may not require approval
        """
        # Tasks that always require approval
        approval_required_tasks = [
            TaskType.CLIENT_COMMUNICATION,
            TaskType.DRAFT_LETTER,
            TaskType.COURT_FILING
        ]

        for task in tasks:
            task_type_str = task.get("task_type")
            try:
                task_type = TaskType(task_type_str)
                if task_type in approval_required_tasks:
                    return ApprovalStatus.PENDING
            except ValueError:
                # Unknown task type, require approval to be safe
                return ApprovalStatus.PENDING

        # Urgent tasks require approval
        for task in tasks:
            if task.get("priority") == "urgent":
                return ApprovalStatus.PENDING

        # If no tasks detected, no approval needed
        if not tasks:
            return ApprovalStatus.NOT_REQUIRED

        # Default: require approval for safety
        return ApprovalStatus.PENDING

    def _generate_proposed_actions(
        self,
        tasks: List[Dict[str, Any]],
        routing_decisions: List[Dict[str, Any]],
        entities: Dict[str, List[str]],
        specialist_responses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate proposed actions/artifacts for human review

        Returns draft outputs that are gated by HUMAN_APPROVAL
        """
        proposed = []

        for task, routing, spec_response in zip(tasks, routing_decisions, specialist_responses):
            action = {
                "task_id": task["id"],
                "action_type": task["task_type"],
                "assigned_agent": routing["agent_name"],
                "confidence": routing["confidence"],
                "status": ApprovalStatus.PENDING.value,
                "ai_generated_response": spec_response.get("response"),
                "proposed_artifact": self._generate_draft_artifact(task, entities),
                "approval_note": "✓ AI has generated a response. Review before sending to client."
            }
            proposed.append(action)

        return proposed

    def _generate_draft_artifact(
        self,
        task: Dict[str, Any],
        entities: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Generate a draft artifact for the task"""
        task_type = task.get("task_type")

        if task_type == TaskType.RETRIEVE_RECORDS.value:
            providers = task.get("extracted_data", {}).get("providers", [])
            return {
                "type": "records_request",
                "draft": f"Draft request for medical records from: {', '.join(providers) if providers else '[Provider Name]'}",
                "requires_review": True
            }

        elif task_type == TaskType.CLIENT_COMMUNICATION.value:
            return {
                "type": "client_message",
                "draft": "Draft client message will be generated by Communication Guru specialist",
                "requires_review": True
            }

        elif task_type == TaskType.SCHEDULE_APPOINTMENT.value:
            return {
                "type": "scheduling",
                "draft": "Appointment scheduling options will be proposed by Voice Scheduler",
                "requires_review": True
            }

        return {
            "type": "general",
            "draft": f"Proposed action for {task_type}",
            "requires_review": True
        }

    def _record_processing(self, response: Dict[str, Any]):
        """Record processing in history for analytics"""
        self.processing_history.append({
            "processing_id": response["processing_id"],
            "case_id": response.get("case_id"),
            "source_type": response["source_type"],
            "tasks_detected": len(response["detected_tasks"]),
            "processed_at": response["processed_at"]
        })

    def get_processing_history(
        self,
        case_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get processing history, optionally filtered by case"""
        if case_id:
            history = [
                h for h in self.processing_history
                if h.get("case_id") == case_id
            ]
        else:
            history = self.processing_history

        return history[-limit:]
