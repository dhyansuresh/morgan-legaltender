"""
Gemini-Powered Intelligent Task Router

Uses Google Gemini AI to intelligently select the best specialist
for each task, going beyond simple pattern matching.
"""

import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai

from .advanced_router import TaskRouter, AgentType, TaskType


class GeminiTaskRouter(TaskRouter):
    """
    Enhanced task router that uses Gemini AI for intelligent agent selection

    Features:
    - AI-powered routing decisions beyond pattern matching
    - Context-aware specialist selection
    - Natural language understanding of task requirements
    - Confidence scoring based on AI analysis
    """

    def __init__(self, use_ai_routing: bool = True):
        """
        Initialize Gemini-powered router

        Args:
            use_ai_routing: Whether to use AI for routing (falls back to rule-based if False)
        """
        super().__init__()

        self.use_ai_routing = use_ai_routing
        self.gemini_model = None

        # Initialize Gemini if API key is available
        if use_ai_routing:
            api_key = os.getenv("GOOGLE_AI_API_KEY")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
                    print("✓ Gemini-powered task routing enabled")
                except Exception as e:
                    print(f"⚠️ Failed to initialize Gemini routing: {e}")
                    print("   Falling back to rule-based routing")
                    self.use_ai_routing = False
            else:
                print("⚠️ No GOOGLE_AI_API_KEY found - using rule-based routing")
                self.use_ai_routing = False

    async def route_task(
        self,
        task: Dict[str, Any],
        consider_load: bool = False
    ) -> Dict[str, Any]:
        """
        Route a task using AI-powered decision making

        Falls back to rule-based routing if AI is unavailable
        """
        if not self.use_ai_routing or not self.gemini_model:
            # Fall back to parent's rule-based routing
            return await super().route_task(task, consider_load)

        try:
            # Use Gemini AI to select the best agent
            routing_decision = await self._ai_route_task(task, consider_load)

            # Record routing decision
            self._record_routing(task, routing_decision)

            # Update agent load
            agent_id_str = routing_decision["agent_id"]
            agent_id = AgentType(agent_id_str)
            self.agents[agent_id]["current_load"] += 1

            return routing_decision

        except Exception as e:
            print(f"⚠️ AI routing failed: {e}, falling back to rule-based")
            return await super().route_task(task, consider_load)

    async def _ai_route_task(
        self,
        task: Dict[str, Any],
        consider_load: bool
    ) -> Dict[str, Any]:
        """
        Use Gemini AI to intelligently route the task
        """
        # Build context for AI
        task_description = task.get("description", "")
        task_type = task.get("task_type", "")
        extracted_data = task.get("extracted_data", {})
        priority = task.get("priority", "medium")

        # Get available agents
        available_agents = self._get_available_agents_info(consider_load, priority)

        # Create prompt for Gemini
        prompt = self._build_routing_prompt(
            task_description,
            task_type,
            extracted_data,
            priority,
            available_agents
        )

        # Get AI recommendation
        response = self.gemini_model.generate_content(prompt)
        ai_decision = self._parse_ai_response(response.text)

        # Validate and build routing decision
        agent_id_str = ai_decision.get("agent_id")

        # Ensure valid agent ID
        try:
            agent_id = AgentType(agent_id_str)
        except ValueError:
            # Invalid agent, fall back to rule-based
            print(f"⚠️ AI suggested invalid agent '{agent_id_str}', using rule-based fallback")
            return await super().route_task(task, consider_load)

        agent_info = self.agents[agent_id]

        routing_decision = {
            "agent_id": agent_id.value,
            "agent_name": agent_info["name"],
            "confidence": ai_decision.get("confidence", 0.9),
            "reasoning": ai_decision.get("reasoning", "AI-selected based on task analysis"),
            "estimated_completion_time": agent_info["average_completion_time"],
            "agent_specialties": agent_info["specialties"],
            "routed_at": self._get_timestamp(),
            "routing_method": "gemini_ai"
        }

        return routing_decision

    def _build_routing_prompt(
        self,
        task_description: str,
        task_type: str,
        extracted_data: Dict[str, Any],
        priority: str,
        available_agents: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Build a prompt for Gemini to make routing decision
        """
        prompt = f"""You are an intelligent task routing system for a legal case management platform.

Your job is to select the BEST AI specialist to handle a specific task.

TASK DETAILS:
- Description: {task_description}
- Type: {task_type}
- Priority: {priority}
- Extracted Information: {json.dumps(extracted_data, indent=2)}

AVAILABLE SPECIALISTS:
"""

        for agent_id, agent_info in available_agents.items():
            prompt += f"""
{agent_id.upper()}:
- Name: {agent_info['name']}
- Specialties: {', '.join(agent_info['specialties'])}
- Average completion time: {agent_info['avg_time']} seconds
- Current load: {agent_info['load']}/{agent_info['max_load']} tasks
"""

        prompt += """

INSTRUCTIONS:
1. Analyze the task description and extracted information
2. Match it to the specialist whose expertise best fits the task
3. Consider the specialist's current workload if relevant
4. Provide your decision in STRICT JSON format

RESPOND WITH ONLY THIS JSON (no other text):
{
  "agent_id": "one of: records_wrangler, communication_guru, legal_researcher, voice_scheduler, evidence_sorter",
  "confidence": 0.0-1.0 (how confident you are in this choice),
  "reasoning": "brief explanation of why this specialist is best suited"
}

JSON RESPONSE:"""

        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini's JSON response
        """
        try:
            # Try to extract JSON from response
            # Sometimes AI adds extra text, so we look for JSON block
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")

        except Exception as e:
            print(f"⚠️ Failed to parse AI response: {e}")
            print(f"   Response was: {response_text}")
            # Return default that will trigger fallback
            return {
                "agent_id": "communication_guru",
                "confidence": 0.5,
                "reasoning": "Failed to parse AI response"
            }

    def _get_available_agents_info(
        self,
        consider_load: bool,
        priority: str
    ) -> Dict[AgentType, Dict[str, Any]]:
        """
        Get simplified agent information for the prompt
        """
        agents_info = {}

        for agent_id, agent_data in self.agents.items():
            agents_info[agent_id] = {
                "name": agent_data["name"],
                "specialties": agent_data["specialties"],
                "avg_time": agent_data["average_completion_time"],
                "load": agent_data["current_load"],
                "max_load": agent_data["max_concurrent_tasks"],
                "enabled": agent_data["enabled"]
            }

        return agents_info

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
