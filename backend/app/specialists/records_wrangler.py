"""
Records Wrangler AI Specialist

Responsibilities:
- Pull missing bills or records from client messages
- Reconcile medical records ledgers
- Draft outreach letters to medical providers
- Track record requests and follow-ups
- Identify gaps in documentation
"""

from typing import List, Optional, Dict, Any
import re
from datetime import datetime


class RecordsAdapter:
    """Adapter interface for LLM provider"""

    async def complete(self, prompt: str) -> str:  # pragma: no cover
        raise NotImplementedError()


class MockRecordsAdapter(RecordsAdapter):
    """Mock adapter for testing"""

    async def complete(self, prompt: str) -> str:
        return (
            "Records Request:\n"
            "To: [Medical Provider]\n"
            "Re: Release of Medical Records\n\n"
            "We are requesting complete medical records and itemized billing "
            "statements for the dates of treatment. Please provide all documentation "
            "including diagnostic imaging, treatment notes, and prescriptions."
        )


class RecordsWrangler:
    """
    AI Specialist for managing medical records and billing documents

    Key capabilities:
    - Identify missing records from case files
    - Draft HIPAA-compliant record requests
    - Generate provider outreach letters
    - Track billing discrepancies
    - Suggest record organization strategies
    """

    def __init__(self, llm_adapter: Optional[RecordsAdapter] = None):
        self.llm = llm_adapter or MockRecordsAdapter()

    def _identify_providers(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract medical provider information from text

        Returns list of providers with details
        """
        providers = []

        # Pattern for Dr. Name
        doctor_pattern = r'\b(?:Dr\.|Doctor|Physician)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        doctors = re.findall(doctor_pattern, text)

        for doctor in set(doctors):
            providers.append({
                "name": f"Dr. {doctor}",
                "type": "physician",
                "confidence": 0.85
            })

        # Pattern for medical facilities
        facility_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Hospital|Clinic|Medical Center|Health|Urgent Care|ER)\b'
        facilities = re.findall(facility_pattern, text)

        for facility in set(facilities):
            providers.append({
                "name": f"{facility} Hospital/Clinic",
                "type": "facility",
                "confidence": 0.80
            })

        return providers

    def _identify_missing_records(
        self,
        text: str,
        existing_records: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Identify what records are mentioned but might be missing

        Args:
            text: Client message or case notes
            existing_records: List of records already on file

        Returns:
            List of potentially missing records with details
        """
        existing_records = existing_records or []
        missing = []

        # Medical record types to look for
        record_types = {
            "MRI": r'\bMRI\b',
            "CT scan": r'\bCT\s+scan\b',
            "X-ray": r'\bX-?ray\b',
            "Ultrasound": r'\bultrasound\b',
            "Medical records": r'\bmedical\s+records\b',
            "Billing statements": r'\b(?:bills?|billing|statements?|invoices?)\b',
            "Prescription records": r'\bprescription\b',
            "Surgery notes": r'\bsurgery\b',
            "Therapy records": r'\b(?:therapy|PT|physical therapy)\b',
            "ER records": r'\b(?:ER|emergency room|emergency department)\b'
        }

        for record_type, pattern in record_types.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Check if not in existing records
                if not any(record_type.lower() in record.lower() for record in existing_records):
                    missing.append({
                        "record_type": record_type,
                        "mentioned_in_text": True,
                        "priority": self._determine_record_priority(record_type),
                        "status": "needed"
                    })

        return missing

    def _determine_record_priority(self, record_type: str) -> str:
        """Determine priority for obtaining a record type"""
        high_priority = ["Surgery notes", "Medical records", "ER records"]
        medium_priority = ["MRI", "CT scan", "X-ray"]

        if record_type in high_priority:
            return "high"
        elif record_type in medium_priority:
            return "medium"
        return "low"

    def _identify_billing_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Identify billing-related mentions

        Returns list of billing items found
        """
        billing_items = []

        # Look for monetary amounts
        money_pattern = r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        amounts = re.findall(money_pattern, text)

        for amount in amounts:
            billing_items.append({
                "amount": amount,
                "type": "charge",
                "requires_itemization": True
            })

        # Look for insurance mentions
        if re.search(r'\b(?:insurance|co-?pay|deductible|out of pocket)\b', text, re.IGNORECASE):
            billing_items.append({
                "type": "insurance_related",
                "requires_policy_info": True
            })

        return billing_items

    async def analyze_records_needs(
        self,
        text: str,
        case_id: Optional[str] = None,
        existing_records: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main analysis method - identifies record needs and gaps

        Args:
            text: Client message or case notes
            case_id: Associated case ID
            existing_records: List of records already obtained

        Returns:
            Dictionary with:
                - identified_providers: Medical providers mentioned
                - missing_records: Records that need to be obtained
                - billing_items: Billing-related items found
                - suggested_actions: Recommended next steps
                - draft_requests: Pre-drafted record request letters
        """
        existing_records = existing_records or []

        # Identify all providers
        providers = self._identify_providers(text)

        # Identify missing records
        missing_records = self._identify_missing_records(text, existing_records)

        # Identify billing items
        billing_items = self._identify_billing_items(text)

        # Generate suggested actions
        suggested_actions = []
        if providers:
            suggested_actions.append(
                f"Request records from {len(providers)} identified provider(s)"
            )
        if missing_records:
            suggested_actions.append(
                f"Obtain {len(missing_records)} missing record type(s)"
            )
        if billing_items:
            suggested_actions.append(
                "Request itemized billing statements to reconcile charges"
            )
        if not (providers or missing_records or billing_items):
            suggested_actions.append(
                "No immediate record gaps detected - flag for human review"
            )

        # Generate draft request letters using LLM
        draft_requests = []
        for provider in providers[:3]:  # Limit to top 3 providers
            prompt = f"""
            Draft a professional, HIPAA-compliant letter requesting medical records.

            Provider: {provider['name']}
            Case ID: {case_id or '[Case Number]'}

            The letter should:
            1. Request complete medical records and billing
            2. Specify authorization is attached
            3. Request records in a specific format
            4. Be professional and clear

            Keep it concise (3-4 paragraphs).
            """
            draft_letter = await self.llm.complete(prompt)

            draft_requests.append({
                "provider": provider['name'],
                "letter_type": "records_request",
                "draft": draft_letter,
                "requires_approval": True
            })

        return {
            "case_id": case_id,
            "analyzed_at": datetime.utcnow().isoformat(),
            "identified_providers": providers,
            "missing_records": missing_records,
            "billing_items": billing_items,
            "suggested_actions": suggested_actions,
            "draft_requests": draft_requests,
            "summary": f"Found {len(providers)} provider(s), {len(missing_records)} missing record type(s), and {len(billing_items)} billing item(s)"
        }

    async def draft_provider_outreach(
        self,
        provider_name: str,
        record_types: List[str],
        case_id: Optional[str] = None,
        patient_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Draft a specific outreach letter to a medical provider

        Args:
            provider_name: Name of the medical provider
            record_types: Types of records being requested
            case_id: Case reference number
            patient_name: Patient name (if known)

        Returns:
            Draft letter and metadata
        """
        record_list = ", ".join(record_types)

        prompt = f"""
        Draft a professional medical records request letter.

        To: {provider_name}
        Patient: {patient_name or '[Patient Name]'}
        Case Reference: {case_id or '[Case Number]'}

        Requesting: {record_list}

        Include:
        - Formal request for records
        - List specific record types needed
        - Mention attached HIPAA authorization
        - Request itemized billing
        - Provide return instructions
        - Professional tone

        Format as a complete business letter.
        """

        draft_letter = await self.llm.complete(prompt)

        return {
            "letter_type": "provider_outreach",
            "provider": provider_name,
            "record_types_requested": record_types,
            "draft": draft_letter,
            "requires_human_approval": True,
            "next_steps": [
                "Review and approve draft",
                "Attach HIPAA authorization form",
                "Send via certified mail or secure fax",
                "Track response deadline"
            ],
            "generated_at": datetime.utcnow().isoformat()
        }

    def track_record_status(
        self,
        requested_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Track status of record requests

        Args:
            requested_records: List of record requests with status

        Returns:
            Summary of outstanding/complete requests
        """
        outstanding = []
        complete = []
        overdue = []

        for record in requested_records:
            status = record.get("status", "pending")
            requested_date = record.get("requested_date")

            if status == "received":
                complete.append(record)
            elif status == "pending":
                # Check if overdue (simplified - would use actual date logic)
                if requested_date:
                    overdue.append(record)
                else:
                    outstanding.append(record)

        return {
            "total_requests": len(requested_records),
            "complete": len(complete),
            "outstanding": len(outstanding),
            "overdue": len(overdue),
            "completion_rate": round(len(complete) / len(requested_records) * 100, 1) if requested_records else 0,
            "summary": f"{len(complete)}/{len(requested_records)} records received",
            "next_actions": [
                f"Follow up on {len(overdue)} overdue request(s)" if overdue else None,
                f"Monitor {len(outstanding)} outstanding request(s)" if outstanding else None
            ]
        }
