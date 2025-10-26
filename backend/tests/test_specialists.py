"""
Tests for AI Specialist Agents
"""

import pytest
from app.specialists.records_wrangler import RecordsWrangler
from app.specialists.voice_scheduler import VoiceScheduler
from app.specialists.evidence_sorter import EvidenceSorter


@pytest.fixture
def records_wrangler():
    """Create Records Wrangler instance"""
    return RecordsWrangler()


@pytest.fixture
def voice_scheduler():
    """Create Voice Scheduler instance"""
    return VoiceScheduler()


@pytest.fixture
def evidence_sorter():
    """Create Evidence Sorter instance"""
    return EvidenceSorter()


class TestRecordsWrangler:
    """Test Records Wrangler specialist"""

    @pytest.mark.asyncio
    async def test_analyze_records_needs(self, records_wrangler):
        """Test records needs analysis"""
        text = "I had an MRI at City Hospital and saw Dr. Johnson. The bill was $3,500."

        result = await records_wrangler.analyze_records_needs(
            text=text,
            case_id="TEST-001"
        )

        assert "identified_providers" in result
        assert "missing_records" in result
        assert "billing_items" in result
        assert "suggested_actions" in result
        assert len(result["identified_providers"]) > 0

    @pytest.mark.asyncio
    async def test_identify_multiple_providers(self, records_wrangler):
        """Test identifying multiple providers"""
        text = "I saw Dr. Smith and Dr. Jones at Memorial Hospital and City Clinic."

        result = await records_wrangler.analyze_records_needs(text=text)

        providers = result["identified_providers"]
        # Should find at least 2 providers
        assert len(providers) >= 2

    @pytest.mark.asyncio
    async def test_draft_provider_outreach(self, records_wrangler):
        """Test drafting provider outreach letter"""
        result = await records_wrangler.draft_provider_outreach(
            provider_name="Dr. Smith",
            record_types=["MRI", "Treatment Notes"],
            case_id="TEST-001",
            patient_name="John Doe"
        )

        assert "draft" in result
        assert "requires_human_approval" in result
        assert result["requires_human_approval"] is True
        assert "next_steps" in result

    @pytest.mark.asyncio
    async def test_detect_missing_records(self, records_wrangler):
        """Test missing records detection"""
        text = "I had an MRI and X-ray done. Also got prescriptions for pain medication."
        existing = ["Initial consultation notes"]

        result = await records_wrangler.analyze_records_needs(
            text=text,
            existing_records=existing
        )

        missing = result["missing_records"]
        # Should detect MRI, X-ray, and prescription as missing
        assert len(missing) > 0


class TestVoiceScheduler:
    """Test Voice Scheduler specialist"""

    @pytest.mark.asyncio
    async def test_parse_scheduling_request(self, voice_scheduler):
        """Test parsing a scheduling request"""
        text = "We need to schedule the deposition for next Tuesday afternoon."

        result = await voice_scheduler.parse_scheduling_request(
            text=text,
            case_id="TEST-001"
        )

        assert "appointment_type" in result
        assert result["appointment_type"] == "deposition"
        assert "date_time_preferences" in result
        assert "required_participants" in result

    @pytest.mark.asyncio
    async def test_detect_appointment_type(self, voice_scheduler):
        """Test detecting different appointment types"""
        test_cases = [
            ("Schedule a mediation", "mediation"),
            ("Book a client consultation", "consultation"),
            ("Need to set up a deposition", "deposition")
        ]

        for text, expected_type in test_cases:
            result = await voice_scheduler.parse_scheduling_request(text=text)
            assert result["appointment_type"] == expected_type

    @pytest.mark.asyncio
    async def test_generate_scheduling_options(self, voice_scheduler):
        """Test generating scheduling options"""
        result = await voice_scheduler.generate_scheduling_options(
            appointment_type="consultation",
            duration_minutes=30
        )

        assert len(result) > 0
        # Each option should have required fields
        for slot in result:
            assert "slot_id" in slot
            assert "datetime" in slot
            assert "display" in slot
            assert "duration_minutes" in slot

    @pytest.mark.asyncio
    async def test_draft_scheduling_message(self, voice_scheduler):
        """Test drafting a scheduling message"""
        slots = await voice_scheduler.generate_scheduling_options("meeting")

        result = await voice_scheduler.draft_scheduling_message(
            recipient_name="John Doe",
            appointment_type="client_meeting",
            proposed_slots=slots[:3],
            case_id="TEST-001"
        )

        assert "draft" in result
        assert "subject" in result
        assert "requires_approval" in result
        assert result["requires_approval"] is True

    @pytest.mark.asyncio
    async def test_detect_urgency(self, voice_scheduler):
        """Test urgency detection"""
        urgent_text = "Need to schedule ASAP - urgent deadline!"

        result = await voice_scheduler.parse_scheduling_request(text=urgent_text)

        assert result["urgency"] == "urgent"

    @pytest.mark.asyncio
    async def test_draft_confirmation_message(self, voice_scheduler):
        """Test drafting confirmation message"""
        slots = await voice_scheduler.generate_scheduling_options("deposition")
        confirmed_slot = slots[0]

        result = await voice_scheduler.draft_confirmation_message(
            recipient_name="Jane Smith",
            confirmed_slot=confirmed_slot,
            appointment_type="deposition",
            location="Conference Room A"
        )

        assert "draft" in result
        assert "calendar_invite" in result
        assert result["requires_approval"] is True


class TestEvidenceSorter:
    """Test Evidence Sorter specialist"""

    @pytest.mark.asyncio
    async def test_analyze_medical_document(self, evidence_sorter):
        """Test analyzing a medical document"""
        result = await evidence_sorter.analyze_document(
            filename="medical_records_dr_smith.pdf",
            text_content="Patient: John Doe. Date: 01/15/2024. Diagnosis: Herniated disc.",
            file_size=125000,
            case_id="TEST-001"
        )

        assert "classification" in result
        assert "metadata" in result
        assert "suggested_tags" in result
        assert "filing_recommendation" in result
        # Should classify as medical
        assert result["classification"]["primary_category"] == "medical"

    @pytest.mark.asyncio
    async def test_classify_legal_document(self, evidence_sorter):
        """Test classifying a legal document"""
        result = await evidence_sorter.analyze_document(
            filename="complaint.pdf",
            text_content="Plaintiff hereby files this complaint for negligence...",
            case_id="TEST-001"
        )

        classification = result["classification"]
        assert classification["primary_category"] == "legal"

    @pytest.mark.asyncio
    async def test_extract_metadata(self, evidence_sorter):
        """Test metadata extraction"""
        text = "Date: 01/15/2024. Amount: $2,500.00. Treatment provided."

        result = await evidence_sorter.analyze_document(
            filename="bill_hospital.pdf",
            text_content=text,
            file_size=50000
        )

        metadata = result["metadata"]
        assert "extracted_dates" in metadata
        assert "extracted_amounts" in metadata
        assert len(metadata["extracted_dates"]) > 0
        assert len(metadata["extracted_amounts"]) > 0

    @pytest.mark.asyncio
    async def test_process_batch(self, evidence_sorter):
        """Test batch document processing"""
        documents = [
            {
                "filename": "medical_bill.pdf",
                "text_content": "Hospital bill for services. Amount: $5,000",
                "file_size": 75000
            },
            {
                "filename": "mri_results.pdf",
                "text_content": "MRI scan results showing herniated disc",
                "file_size": 150000
            },
            {
                "filename": "demand_letter.docx",
                "text_content": "Settlement demand for $100,000",
                "file_size": 25000
            }
        ]

        result = await evidence_sorter.process_batch(
            documents=documents,
            case_id="TEST-001"
        )

        assert "total_documents" in result
        assert result["total_documents"] == 3
        assert "category_breakdown" in result
        assert "documents" in result
        assert len(result["documents"]) == 3

    @pytest.mark.asyncio
    async def test_duplicate_detection(self, evidence_sorter):
        """Test duplicate document detection"""
        same_content = "This is identical content"

        documents = [
            {"filename": "doc1.pdf", "text_content": same_content, "file_size": 1000},
            {"filename": "doc2.pdf", "text_content": same_content, "file_size": 1000},
            {"filename": "doc3.pdf", "text_content": "Different content", "file_size": 1000}
        ]

        result = await evidence_sorter.process_batch(documents=documents)

        # Should detect one duplicate
        assert result["duplicates_found"] > 0

    @pytest.mark.asyncio
    async def test_generate_salesforce_payload(self, evidence_sorter):
        """Test Salesforce payload generation"""
        doc_analysis = await evidence_sorter.analyze_document(
            filename="test_doc.pdf",
            text_content="Medical record content",
            case_id="TEST-001"
        )

        payload = evidence_sorter.generate_salesforce_payload(doc_analysis)

        assert "Title" in payload
        assert "Category__c" in payload
        assert "Case_ID__c" in payload
        assert payload["Case_ID__c"] == "TEST-001"

    @pytest.mark.asyncio
    async def test_suggest_tags(self, evidence_sorter):
        """Test tag suggestion"""
        result = await evidence_sorter.analyze_document(
            filename="urgent_medical_bill.pdf",
            text_content="Urgent: Hospital bill due immediately. Amount: $10,000",
            case_id="TEST-001"
        )

        tags = result["suggested_tags"]
        # Should suggest urgent and billing tags
        assert "medical" in tags or "billing" in tags
        assert len(tags) > 0


class TestSpecialistIntegration:
    """Test integration between specialists"""

    @pytest.mark.asyncio
    async def test_records_to_sorter_workflow(self, records_wrangler, evidence_sorter):
        """Test workflow from records request to document organization"""
        # Step 1: Identify records needs
        text = "I had an MRI at City Hospital"
        records_result = await records_wrangler.analyze_records_needs(text=text)

        assert len(records_result["missing_records"]) > 0

        # Step 2: When records arrive, classify them
        doc_result = await evidence_sorter.analyze_document(
            filename="mri_results.pdf",
            text_content="MRI scan results",
            case_id="TEST-001"
        )

        assert doc_result["classification"]["primary_category"] == "medical"
