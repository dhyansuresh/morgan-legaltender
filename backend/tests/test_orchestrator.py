"""
Tests for the Tender Orchestrator
"""

import pytest
from orchestrator.tender_orchestrator import TenderOrchestrator, SourceType, ApprovalStatus
from orchestrator.advanced_router import TaskRouter


@pytest.fixture
def orchestrator():
    """Create a fresh orchestrator instance for each test"""
    return TenderOrchestrator()


@pytest.fixture
def sample_email_text():
    """Sample messy email text"""
    return """
    Hi,

    I had my MRI done at Dr. Smith's office yesterday and the results showed a herniated disc.
    The bill was $2,500 and I'm not sure if my insurance will cover it.

    Also, can we schedule a meeting next week to discuss my case? Tuesday or Wednesday afternoon works best for me.

    The accident happened on 01/15/2024 and I'm still having back pain.

    Thanks,
    John Doe
    john.doe@email.com
    555-123-4567
    """


@pytest.fixture
def sample_sms_text():
    """Sample SMS text"""
    return "Dr said I need surgery. Bill is $5000. When can we talk?"


class TestOrchestratorBasic:
    """Test basic orchestrator functionality"""

    @pytest.mark.asyncio
    async def test_process_email_input(self, orchestrator, sample_email_text):
        """Test processing an email input"""
        result = await orchestrator.process_input(
            raw_text=sample_email_text,
            source_type=SourceType.EMAIL,
            case_id="TEST-001"
        )

        assert result["case_id"] == "TEST-001"
        assert result["source_type"] == "email"
        assert "normalized_text" in result
        assert "extracted_entities" in result
        assert "detected_tasks" in result
        assert "routing_decisions" in result

    @pytest.mark.asyncio
    async def test_process_sms_input(self, orchestrator, sample_sms_text):
        """Test processing an SMS input"""
        result = await orchestrator.process_input(
            raw_text=sample_sms_text,
            source_type=SourceType.SMS,
            case_id="TEST-002"
        )

        assert result["source_type"] == "sms"
        assert len(result["detected_tasks"]) > 0


class TestEntityExtraction:
    """Test entity extraction functionality"""

    @pytest.mark.asyncio
    async def test_extract_medical_terms(self, orchestrator, sample_email_text):
        """Test extraction of medical terms"""
        result = await orchestrator.process_input(
            raw_text=sample_email_text,
            source_type=SourceType.EMAIL
        )

        entities = result["extracted_entities"]
        assert "medical_terms" in entities
        assert len(entities["medical_terms"]) > 0

    @pytest.mark.asyncio
    async def test_extract_contact_info(self, orchestrator, sample_email_text):
        """Test extraction of contact information"""
        result = await orchestrator.process_input(
            raw_text=sample_email_text,
            source_type=SourceType.EMAIL
        )

        entities = result["extracted_entities"]
        assert "contact_info" in entities
        # Should find email and phone
        assert len(entities["contact_info"]) >= 2

    @pytest.mark.asyncio
    async def test_extract_dates(self, orchestrator, sample_email_text):
        """Test extraction of dates"""
        result = await orchestrator.process_input(
            raw_text=sample_email_text,
            source_type=SourceType.EMAIL
        )

        entities = result["extracted_entities"]
        assert "dates" in entities
        assert len(entities["dates"]) > 0

    @pytest.mark.asyncio
    async def test_extract_monetary_amounts(self, orchestrator, sample_email_text):
        """Test extraction of monetary amounts"""
        result = await orchestrator.process_input(
            raw_text=sample_email_text,
            source_type=SourceType.EMAIL
        )

        entities = result["extracted_entities"]
        assert "monetary_amounts" in entities
        assert len(entities["monetary_amounts"]) > 0


class TestPIIDetection:
    """Test PII/PHI detection functionality"""

    @pytest.mark.asyncio
    async def test_detect_pii(self, orchestrator, sample_email_text):
        """Test PII detection"""
        result = await orchestrator.process_input(
            raw_text=sample_email_text,
            source_type=SourceType.EMAIL
        )

        pii_labels = result["pii_phi_labels"]
        assert "pii" in pii_labels
        assert "phi" in pii_labels
        # Should detect email and phone as PII
        assert len(pii_labels["pii"]) > 0

    @pytest.mark.asyncio
    async def test_detect_phi(self, orchestrator):
        """Test PHI (health information) detection"""
        medical_text = "Patient has herniated disc at L4-L5. MRI shows severe stenosis."

        result = await orchestrator.process_input(
            raw_text=medical_text,
            source_type=SourceType.MANUAL_ENTRY
        )

        pii_labels = result["pii_phi_labels"]
        assert len(pii_labels["phi"]) > 0


class TestTaskDetection:
    """Test task detection functionality"""

    @pytest.mark.asyncio
    async def test_detect_records_task(self, orchestrator):
        """Test detection of records retrieval task"""
        text = "I need to get my medical records from Dr. Johnson's office."

        result = await orchestrator.process_input(
            raw_text=text,
            source_type=SourceType.EMAIL
        )

        tasks = result["detected_tasks"]
        assert len(tasks) > 0
        # Should detect retrieve_records task
        task_types = [t["task_type"] for t in tasks]
        assert "retrieve_records" in task_types

    @pytest.mark.asyncio
    async def test_detect_scheduling_task(self, orchestrator):
        """Test detection of scheduling task"""
        text = "Can we schedule a deposition for next Tuesday?"

        result = await orchestrator.process_input(
            raw_text=text,
            source_type=SourceType.EMAIL
        )

        tasks = result["detected_tasks"]
        task_types = [t["task_type"] for t in tasks]
        assert "schedule_appointment" in task_types

    @pytest.mark.asyncio
    async def test_detect_communication_task(self, orchestrator):
        """Test detection of client communication task"""
        text = "What's the status of my case? I'm confused about the next steps."

        result = await orchestrator.process_input(
            raw_text=text,
            source_type=SourceType.CLIENT_PORTAL
        )

        tasks = result["detected_tasks"]
        task_types = [t["task_type"] for t in tasks]
        assert "client_communication" in task_types

    @pytest.mark.asyncio
    async def test_multiple_tasks_detected(self, orchestrator, sample_email_text):
        """Test detection of multiple tasks from single input"""
        result = await orchestrator.process_input(
            raw_text=sample_email_text,
            source_type=SourceType.EMAIL
        )

        tasks = result["detected_tasks"]
        # Sample email should trigger multiple tasks
        assert len(tasks) >= 2


class TestTaskPriority:
    """Test task priority detection"""

    @pytest.mark.asyncio
    async def test_urgent_priority(self, orchestrator):
        """Test urgent priority detection"""
        text = "URGENT: Need medical records immediately for court deadline tomorrow!"

        result = await orchestrator.process_input(
            raw_text=text,
            source_type=SourceType.EMAIL
        )

        tasks = result["detected_tasks"]
        # Should have at least one urgent task
        priorities = [t["priority"] for t in tasks]
        assert "urgent" in priorities

    @pytest.mark.asyncio
    async def test_high_priority(self, orchestrator):
        """Test high priority detection"""
        text = "Important: Please get these records by Friday."

        result = await orchestrator.process_input(
            raw_text=text,
            source_type=SourceType.EMAIL
        )

        tasks = result["detected_tasks"]
        priorities = [t["priority"] for t in tasks]
        assert "high" in priorities or "urgent" in priorities


class TestApprovalWorkflow:
    """Test approval workflow"""

    @pytest.mark.asyncio
    async def test_approval_required_for_communication(self, orchestrator):
        """Test that client communication requires approval"""
        text = "Please send a message to the client about their case status."

        result = await orchestrator.process_input(
            raw_text=text,
            source_type=SourceType.MANUAL_ENTRY
        )

        # Communication tasks should require approval
        assert result["approval_required"] == ApprovalStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_proposed_actions_generated(self, orchestrator, sample_email_text):
        """Test that proposed actions are generated"""
        result = await orchestrator.process_input(
            raw_text=sample_email_text,
            source_type=SourceType.EMAIL
        )

        assert "proposed_actions" in result
        assert len(result["proposed_actions"]) > 0

        # Each action should require approval
        for action in result["proposed_actions"]:
            assert action["status"] == ApprovalStatus.PENDING.value


class TestRouting:
    """Test task routing integration"""

    @pytest.mark.asyncio
    async def test_tasks_routed_to_specialists(self, orchestrator, sample_email_text):
        """Test that tasks are routed to appropriate specialists"""
        result = await orchestrator.process_input(
            raw_text=sample_email_text,
            source_type=SourceType.EMAIL
        )

        routing_decisions = result["routing_decisions"]
        assert len(routing_decisions) > 0

        # Each routing decision should have required fields
        for routing in routing_decisions:
            assert "agent_id" in routing
            assert "agent_name" in routing
            assert "confidence" in routing
            assert "reasoning" in routing


class TestProcessingHistory:
    """Test processing history tracking"""

    @pytest.mark.asyncio
    async def test_processing_recorded_in_history(self, orchestrator):
        """Test that processing is recorded"""
        text = "Test input"

        await orchestrator.process_input(
            raw_text=text,
            source_type=SourceType.MANUAL_ENTRY,
            case_id="TEST-HISTORY"
        )

        history = orchestrator.get_processing_history()
        assert len(history) > 0
        assert history[-1]["case_id"] == "TEST-HISTORY"

    @pytest.mark.asyncio
    async def test_filter_history_by_case(self, orchestrator):
        """Test filtering history by case ID"""
        # Process two different cases
        await orchestrator.process_input(
            raw_text="Test 1",
            source_type=SourceType.EMAIL,
            case_id="CASE-A"
        )

        await orchestrator.process_input(
            raw_text="Test 2",
            source_type=SourceType.EMAIL,
            case_id="CASE-B"
        )

        # Get history for specific case
        history_a = orchestrator.get_processing_history(case_id="CASE-A")
        assert all(h["case_id"] == "CASE-A" for h in history_a)
