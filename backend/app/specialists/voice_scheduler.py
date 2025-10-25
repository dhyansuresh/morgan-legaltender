"""
Voice Bot Scheduler AI Specialist

Responsibilities:
- Coordinate depositions, mediations, and client check-ins
- Parse scheduling requests from messages
- Identify availability conflicts
- Generate calendar invites
- Draft scheduling confirmation messages
- Send appointment reminders
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import re


class SchedulerAdapter:
    """Adapter interface for LLM provider"""

    async def complete(self, prompt: str) -> str:  # pragma: no cover
        raise NotImplementedError()


class MockSchedulerAdapter(SchedulerAdapter):
    """Mock adapter for testing"""

    async def complete(self, prompt: str) -> str:
        return (
            "Proposed Appointment Schedule:\n\n"
            "Dear [Client Name],\n\n"
            "We would like to schedule a meeting to discuss your case. "
            "We have the following times available:\n"
            "- Tuesday, [Date] at 2:00 PM\n"
            "- Wednesday, [Date] at 10:00 AM\n"
            "- Thursday, [Date] at 3:00 PM\n\n"
            "Please let us know which time works best for you.\n\n"
            "Best regards,\nYour Legal Team"
        )


class VoiceScheduler:
    """
    AI Specialist for scheduling and coordinating appointments

    Key capabilities:
    - Parse scheduling requests from messy text
    - Identify appointment types (deposition, mediation, consultation)
    - Extract date/time preferences
    - Generate scheduling options
    - Draft confirmation messages
    - Create reminder scripts
    """

    def __init__(self, llm_adapter: Optional[SchedulerAdapter] = None):
        self.llm = llm_adapter or MockSchedulerAdapter()

    def _extract_appointment_type(self, text: str) -> str:
        """
        Identify the type of appointment being requested
        """
        appointment_types = {
            "deposition": r'\bdeposition\b',
            "mediation": r'\bmediation\b',
            "consultation": r'\bconsultation\b',
            "client_meeting": r'\b(?:meeting|check-in|update)\b',
            "court_hearing": r'\b(?:hearing|court|trial)\b',
            "medical_appointment": r'\b(?:doctor|medical|exam|IME)\b'
        }

        for appt_type, pattern in appointment_types.items():
            if re.search(pattern, text, re.IGNORECASE):
                return appt_type

        return "general_meeting"

    def _extract_date_time_preferences(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract date and time mentions from text

        Returns list of date/time preferences found
        """
        preferences = []

        # Extract explicit dates
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
            r'\b(?:next week|this week|tomorrow|today)\b'
        ]

        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            for date in dates:
                preferences.append({
                    "type": "date",
                    "value": date,
                    "source": "explicit_mention"
                })

        # Extract time mentions
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b',
            r'\b\d{1,2}\s*(?:AM|PM|am|pm)\b',
            r'\b(?:morning|afternoon|evening|noon)\b'
        ]

        for pattern in time_patterns:
            times = re.findall(pattern, text, re.IGNORECASE)
            for time in times:
                preferences.append({
                    "type": "time",
                    "value": time,
                    "source": "explicit_mention"
                })

        return preferences

    def _extract_participants(self, text: str) -> List[str]:
        """
        Identify who needs to be included in the appointment
        """
        participants = []

        # Look for role mentions
        if re.search(r'\b(?:opposing counsel|defense attorney)\b', text, re.IGNORECASE):
            participants.append("opposing_counsel")

        if re.search(r'\b(?:mediator|arbitrator)\b', text, re.IGNORECASE):
            participants.append("mediator")

        if re.search(r'\b(?:client|plaintiff)\b', text, re.IGNORECASE):
            participants.append("client")

        if re.search(r'\b(?:expert|witness)\b', text, re.IGNORECASE):
            participants.append("expert_witness")

        if re.search(r'\b(?:court reporter|stenographer)\b', text, re.IGNORECASE):
            participants.append("court_reporter")

        return participants

    def _determine_urgency(self, text: str) -> str:
        """Determine scheduling urgency"""
        urgent_keywords = [
            r'\b(?:asap|urgent|emergency|immediately)\b',
            r'\b(?:deadline|due date|must be scheduled)\b'
        ]

        for pattern in urgent_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                return "urgent"

        return "normal"

    def _extract_location_preference(self, text: str) -> Optional[str]:
        """Extract location or format preference"""
        if re.search(r'\b(?:zoom|teams|virtual|video|online)\b', text, re.IGNORECASE):
            return "virtual"
        elif re.search(r'\b(?:in person|office|conference room)\b', text, re.IGNORECASE):
            return "in_person"
        elif re.search(r'\bphone\b', text, re.IGNORECASE):
            return "phone"
        return None

    async def parse_scheduling_request(
        self,
        text: str,
        case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse a scheduling request from text

        Args:
            text: Message containing scheduling request
            case_id: Associated case ID

        Returns:
            Structured scheduling information
        """
        appointment_type = self._extract_appointment_type(text)
        date_time_prefs = self._extract_date_time_preferences(text)
        participants = self._extract_participants(text)
        urgency = self._determine_urgency(text)
        location = self._extract_location_preference(text)

        return {
            "case_id": case_id,
            "appointment_type": appointment_type,
            "urgency": urgency,
            "location_preference": location,
            "date_time_preferences": date_time_prefs,
            "required_participants": participants,
            "parsed_at": datetime.utcnow().isoformat(),
            "requires_confirmation": True
        }

    async def generate_scheduling_options(
        self,
        appointment_type: str,
        duration_minutes: int = 60,
        preferred_dates: Optional[List[str]] = None,
        excluded_dates: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate scheduling options based on availability

        Args:
            appointment_type: Type of appointment
            duration_minutes: Expected duration
            preferred_dates: Preferred date ranges
            excluded_dates: Dates to avoid

        Returns:
            List of available time slots
        """
        # In production, this would check actual calendar availability
        # For now, generate sample options

        options = []
        base_date = datetime.now() + timedelta(days=2)

        # Generate 3-5 options over next 2 weeks
        for i in range(5):
            option_date = base_date + timedelta(days=i * 2)

            # Skip weekends
            if option_date.weekday() >= 5:
                continue

            # Generate morning and afternoon slots
            for hour in [10, 14]:  # 10 AM and 2 PM
                slot_time = option_date.replace(hour=hour, minute=0, second=0)

                options.append({
                    "slot_id": f"SLOT-{int(slot_time.timestamp())}",
                    "datetime": slot_time.isoformat(),
                    "display": slot_time.strftime("%A, %B %d, %Y at %I:%M %p"),
                    "duration_minutes": duration_minutes,
                    "available": True,
                    "appointment_type": appointment_type
                })

        return options[:5]  # Return top 5 options

    async def draft_scheduling_message(
        self,
        recipient_name: Optional[str],
        appointment_type: str,
        proposed_slots: List[Dict[str, Any]],
        case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Draft a scheduling coordination message

        Args:
            recipient_name: Name of recipient
            appointment_type: Type of appointment
            proposed_slots: Available time slots
            case_id: Case reference

        Returns:
            Draft message and metadata
        """
        # Format slot options for prompt
        slot_options = "\n".join([
            f"- {slot['display']}"
            for slot in proposed_slots[:3]
        ])

        prompt = f"""
        Draft a professional scheduling message.

        Recipient: {recipient_name or '[Recipient Name]'}
        Appointment Type: {appointment_type.replace('_', ' ').title()}
        Case: {case_id or '[Case Number]'}

        Available times:
        {slot_options}

        The message should:
        1. Be professional and courteous
        2. Clearly state the purpose
        3. Provide the time options
        4. Ask for confirmation
        5. Provide contact info for questions

        Keep it concise and clear.
        """

        draft_message = await self.llm.complete(prompt)

        return {
            "message_type": "scheduling_request",
            "appointment_type": appointment_type,
            "recipient": recipient_name,
            "proposed_slots": proposed_slots,
            "draft": draft_message,
            "subject": f"Scheduling: {appointment_type.replace('_', ' ').title()}",
            "requires_approval": True,
            "generated_at": datetime.utcnow().isoformat()
        }

    async def draft_confirmation_message(
        self,
        recipient_name: Optional[str],
        confirmed_slot: Dict[str, Any],
        appointment_type: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Draft an appointment confirmation message

        Args:
            recipient_name: Name of recipient
            confirmed_slot: The confirmed time slot
            appointment_type: Type of appointment
            location: Meeting location/link

        Returns:
            Confirmation message draft
        """
        prompt = f"""
        Draft an appointment confirmation message.

        Recipient: {recipient_name or '[Recipient Name]'}
        Appointment: {appointment_type.replace('_', ' ').title()}
        Date/Time: {confirmed_slot.get('display')}
        Location: {location or 'To be confirmed'}

        The message should:
        1. Confirm the appointment details
        2. Provide any preparation instructions
        3. Include location/connection details
        4. Mention any documents to bring
        5. Provide contact for changes

        Professional and helpful tone.
        """

        draft_message = await self.llm.complete(prompt)

        return {
            "message_type": "appointment_confirmation",
            "appointment_type": appointment_type,
            "confirmed_datetime": confirmed_slot.get('datetime'),
            "draft": draft_message,
            "subject": f"Confirmed: {appointment_type.replace('_', ' ').title()}",
            "requires_approval": True,
            "calendar_invite": {
                "summary": f"{appointment_type.replace('_', ' ').title()}",
                "start": confirmed_slot.get('datetime'),
                "duration_minutes": confirmed_slot.get('duration_minutes', 60),
                "location": location
            },
            "generated_at": datetime.utcnow().isoformat()
        }

    async def draft_reminder_message(
        self,
        recipient_name: Optional[str],
        appointment_details: Dict[str, Any],
        hours_before: int = 24
    ) -> Dict[str, Any]:
        """
        Draft an appointment reminder message

        Args:
            recipient_name: Name of recipient
            appointment_details: Appointment information
            hours_before: How many hours before to send

        Returns:
            Reminder message draft
        """
        appt_time = appointment_details.get('datetime', '[Date/Time]')
        appt_type = appointment_details.get('appointment_type', 'appointment')
        location = appointment_details.get('location', 'TBD')

        prompt = f"""
        Draft a friendly appointment reminder.

        Recipient: {recipient_name or '[Recipient Name]'}
        Appointment: {appt_type.replace('_', ' ').title()}
        When: {appt_time}
        Location: {location}

        This is a {hours_before}-hour reminder.

        The message should:
        1. Friendly reminder tone
        2. State the appointment details
        3. Confirm location/connection info
        4. Remind about any preparation needed
        5. Provide contact for questions/changes

        Keep it brief and helpful.
        """

        draft_message = await self.llm.complete(prompt)

        return {
            "message_type": "appointment_reminder",
            "send_time": f"{hours_before} hours before",
            "draft": draft_message,
            "subject": f"Reminder: {appt_type.replace('_', ' ').title()}",
            "requires_approval": False,  # Reminders can be auto-sent
            "generated_at": datetime.utcnow().isoformat()
        }

    def analyze_scheduling_conflicts(
        self,
        requested_slots: List[Dict[str, Any]],
        existing_appointments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze potential scheduling conflicts

        Args:
            requested_slots: Desired time slots
            existing_appointments: Already scheduled appointments

        Returns:
            Conflict analysis and available alternatives
        """
        conflicts = []
        available = []

        for slot in requested_slots:
            has_conflict = False

            # Check against existing appointments
            # (Simplified - would use actual datetime comparison)
            for appt in existing_appointments:
                if appt.get('datetime') == slot.get('datetime'):
                    conflicts.append({
                        "slot": slot,
                        "conflicting_appointment": appt,
                        "severity": "blocked"
                    })
                    has_conflict = True
                    break

            if not has_conflict:
                available.append(slot)

        return {
            "total_slots_analyzed": len(requested_slots),
            "conflicts_found": len(conflicts),
            "available_slots": available,
            "conflicts": conflicts,
            "recommendation": (
                f"Proceed with {len(available)} available slot(s)"
                if available else
                "No slots available - suggest alternative dates"
            )
        }
