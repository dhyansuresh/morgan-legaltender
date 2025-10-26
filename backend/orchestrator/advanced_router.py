
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    """All possible task types the system can detect"""
    RETRIEVE_RECORDS = "retrieve_records"
    CLIENT_COMMUNICATION = "client_communication"
    LEGAL_RESEARCH = "legal_research"
    SCHEDULE_APPOINTMENT = "schedule_appointment"
    DOCUMENT_ORGANIZATION = "document_organization"
    DEADLINE_REMINDER = "deadline_reminder"
    FOLLOW_UP = "follow_up"
    DRAFT_LETTER = "draft_letter"
    COURT_FILING = "court_filing"


class AgentType(str, Enum):
    """AI Specialist Agents"""
    RECORDS_WRANGLER = "records_wrangler"
    COMMUNICATION_GURU = "communication_guru"
    LEGAL_RESEARCHER = "legal_researcher"
    VOICE_SCHEDULER = "voice_scheduler"
    EVIDENCE_SORTER = "evidence_sorter"


class TaskRouter:
    """
    Intelligent task router that assigns tasks to the most appropriate AI specialist
    
    Features:
    - Task type matching
    - Load balancing across agents
    - Priority-based routing
    - Agent availability checking
    """
    
    def __init__(self):
        # Define routing rules: task_type -> preferred agent
        self.routing_rules = {
            TaskType.RETRIEVE_RECORDS: AgentType.RECORDS_WRANGLER,
            TaskType.CLIENT_COMMUNICATION: AgentType.COMMUNICATION_GURU,
            TaskType.LEGAL_RESEARCH: AgentType.LEGAL_RESEARCHER,
            TaskType.SCHEDULE_APPOINTMENT: AgentType.VOICE_SCHEDULER,
            TaskType.DOCUMENT_ORGANIZATION: AgentType.EVIDENCE_SORTER,
            TaskType.DEADLINE_REMINDER: AgentType.COMMUNICATION_GURU,
            TaskType.FOLLOW_UP: AgentType.COMMUNICATION_GURU,
            TaskType.DRAFT_LETTER: AgentType.COMMUNICATION_GURU,
            TaskType.COURT_FILING: AgentType.LEGAL_RESEARCHER,
        }
        
        # Agent configurations
        self.agents = {
            AgentType.RECORDS_WRANGLER: {
                "name": "Records Wrangler",
                "description": "Pulls missing bills or records from client messages",
                "specialties": [
                    "medical_records",
                    "billing_records",
                    "insurance_documents",
                    "provider_outreach"
                ],
                "max_concurrent_tasks": 5,
                "current_load": 0,
                "average_completion_time": 180,  # seconds
                "success_rate": 0.94,
                "enabled": True
            },
            AgentType.COMMUNICATION_GURU: {
                "name": "Client Communication Guru",
                "description": "Drafts clear, empathetic messages to clients",
                "specialties": [
                    "client_messages",
                    "status_updates",
                    "empathetic_responses",
                    "follow_ups"
                ],
                "max_concurrent_tasks": 5,
                "current_load": 0,
                "average_completion_time": 45,
                "success_rate": 0.98,
                "enabled": True
            },
            AgentType.LEGAL_RESEARCHER: {
                "name": "Legal Researcher",
                "description": "Finds supporting verdicts and citations",
                "specialties": [
                    "case_law",
                    "legal_citations",
                    "precedent_analysis",
                    "legal_theories"
                ],
                "max_concurrent_tasks": 3,
                "current_load": 0,
                "average_completion_time": 320,
                "success_rate": 0.91,
                "enabled": True
            },
            AgentType.VOICE_SCHEDULER: {
                "name": "Voice Bot Scheduler",
                "description": "Coordinates depositions, mediations, or client check-ins",
                "specialties": [
                    "appointment_scheduling",
                    "depositions",
                    "mediations",
                    "client_check_ins"
                ],
                "max_concurrent_tasks": 5,
                "current_load": 0,
                "average_completion_time": 90,
                "success_rate": 0.96,
                "enabled": True
            },
            AgentType.EVIDENCE_SORTER: {
                "name": "Evidence Sorter",
                "description": "Extracts and labels attachments for case management",
                "specialties": [
                    "document_sorting",
                    "file_organization",
                    "salesforce_integration",
                    "attachment_labeling"
                ],
                "max_concurrent_tasks": 5,
                "current_load": 0,
                "average_completion_time": 25,
                "success_rate": 0.99,
                "enabled": True
            }
        }
        
        # Track routing history for analytics
        self.routing_history = []
    
    async def route_task(
        self,
        task: Dict[str, Any],
        consider_load: bool = True
    ) -> Dict[str, Any]:
        """
        Route a task to the most appropriate AI specialist
        
        Args:
            task: Dictionary containing task details
                - task_type: Type of task
                - priority: urgent, high, medium, low
                - description: Task description
                - extracted_data: Additional task data
            consider_load: Whether to consider agent load in routing
            
        Returns:
            Dictionary with routing decision:
                - agent_id: ID of assigned agent
                - agent_name: Name of assigned agent
                - confidence: Routing confidence (0.0-1.0)
                - reasoning: Why this agent was chosen
                - estimated_completion_time: Expected time to complete
        """
        task_type = task.get("task_type")
        priority = task.get("priority", "medium")
        
        # Get primary agent based on task type
        primary_agent_id = self._get_primary_agent(task_type)
        
        # Check if primary agent is available
        if consider_load:
            agent_id = self._find_available_agent(primary_agent_id, priority)
        else:
            agent_id = primary_agent_id
        
        agent_info = self.agents[agent_id]
        
        # Calculate routing confidence
        confidence = self._calculate_routing_confidence(
            task_type, 
            agent_id, 
            task.get("extracted_data", {})
        )
        
        # Build routing decision
        routing_decision = {
            "agent_id": agent_id.value,
            "agent_name": agent_info["name"],
            "confidence": confidence,
            "reasoning": self._generate_routing_reasoning(task_type, agent_id, priority),
            "estimated_completion_time": agent_info["average_completion_time"],
            "agent_specialties": agent_info["specialties"],
            "routed_at": datetime.utcnow().isoformat()
        }
        
        # Record routing decision
        self._record_routing(task, routing_decision)
        
        # Update agent load (in production, this would be in database)
        self.agents[agent_id]["current_load"] += 1
        
        return routing_decision
    
    def _get_primary_agent(self, task_type: str) -> AgentType:
        """Get the primary agent for a task type"""
        # Convert string to enum if needed
        if isinstance(task_type, str):
            try:
                task_type_enum = TaskType(task_type)
            except ValueError:
                # Unknown task type, default to Communication Guru
                return AgentType.COMMUNICATION_GURU
        else:
            task_type_enum = task_type
        
        return self.routing_rules.get(
            task_type_enum, 
            AgentType.COMMUNICATION_GURU
        )
    
    def _find_available_agent(
        self, 
        preferred_agent: AgentType, 
        priority: str
    ) -> AgentType:
        """
        Find an available agent, considering load balancing
        
        If preferred agent is at capacity:
        - For urgent/high priority: still assign to preferred agent
        - For medium/low priority: try to find alternative agent
        """
        agent = self.agents[preferred_agent]
        
        # Check if agent is enabled
        if not agent["enabled"]:
            return self._find_fallback_agent(preferred_agent)
        
        # Check if agent is at capacity
        if agent["current_load"] >= agent["max_concurrent_tasks"]:
            # For urgent tasks, assign anyway (overload if necessary)
            if priority in ["urgent", "high"]:
                return preferred_agent
            
            # For lower priority, try to find alternative
            return self._find_fallback_agent(preferred_agent)
        
        return preferred_agent
    
    def _find_fallback_agent(self, primary_agent: AgentType) -> AgentType:
        """
        Find a fallback agent when primary is unavailable
        
        Strategy: Find agent with lowest current load
        """
        available_agents = [
            (agent_id, info) 
            for agent_id, info in self.agents.items()
            if info["enabled"] and info["current_load"] < info["max_concurrent_tasks"]
        ]
        
        if not available_agents:
            # All agents at capacity, return primary anyway
            return primary_agent
        
        # Return agent with lowest load
        fallback_agent = min(available_agents, key=lambda x: x[1]["current_load"])
        return fallback_agent[0]
    
    def _calculate_routing_confidence(
        self,
        task_type: str,
        agent_id: AgentType,
        extracted_data: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for this routing decision
        
        Factors:
        - Direct match between task type and agent specialty: high confidence
        - Agent success rate
        - Agent current load
        """
        base_confidence = 0.8
        
        # Boost confidence if task type directly maps to agent
        if task_type in [t.value for t in TaskType]:
            primary_agent = self._get_primary_agent(task_type)
            if agent_id == primary_agent:
                base_confidence = 0.95
        
        # Adjust based on agent success rate
        agent_success_rate = self.agents[agent_id]["success_rate"]
        confidence = base_confidence * agent_success_rate
        
        # Reduce confidence if agent is near capacity
        agent = self.agents[agent_id]
        load_ratio = agent["current_load"] / agent["max_concurrent_tasks"]
        if load_ratio > 0.8:
            confidence *= 0.9
        
        return round(confidence, 2)
    
    def _generate_routing_reasoning(
        self,
        task_type: str,
        agent_id: AgentType,
        priority: str
    ) -> str:
        """Generate human-readable reasoning for routing decision"""
        agent_name = self.agents[agent_id]["name"]
        
        primary_agent = self._get_primary_agent(task_type)
        
        if agent_id == primary_agent:
            return f"{agent_name} is the primary specialist for {task_type} tasks"
        else:
            return f"Routed to {agent_name} due to load balancing (priority: {priority})"
    
    def _record_routing(
        self,
        task: Dict[str, Any],
        routing_decision: Dict[str, Any]
    ):
        """Record routing decision for analytics"""
        self.routing_history.append({
            "task_id": task.get("id"),
            "task_type": task.get("task_type"),
            "priority": task.get("priority"),
            "agent_id": routing_decision["agent_id"],
            "confidence": routing_decision["confidence"],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current status of agents
        
        Args:
            agent_id: Specific agent ID, or None for all agents
        """
        if agent_id:
            agent_enum = AgentType(agent_id)
            agent = self.agents[agent_enum]
            return {
                "agent_id": agent_id,
                "name": agent["name"],
                "current_load": agent["current_load"],
                "max_concurrent_tasks": agent["max_concurrent_tasks"],
                "capacity_percentage": round(
                    (agent["current_load"] / agent["max_concurrent_tasks"]) * 100, 
                    1
                ),
                "enabled": agent["enabled"],
                "success_rate": agent["success_rate"]
            }
        else:
            # Return status for all agents
            return {
                agent_id.value: {
                    "name": info["name"],
                    "current_load": info["current_load"],
                    "max_concurrent_tasks": info["max_concurrent_tasks"],
                    "capacity_percentage": round(
                        (info["current_load"] / info["max_concurrent_tasks"]) * 100,
                        1
                    ),
                    "enabled": info["enabled"],
                    "success_rate": info["success_rate"]
                }
                for agent_id, info in self.agents.items()
            }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics for analytics"""
        if not self.routing_history:
            return {
                "total_routed": 0,
                "by_agent": {},
                "by_task_type": {},
                "average_confidence": 0.0
            }
        
        total = len(self.routing_history)
        
        # Count by agent
        by_agent = {}
        by_task_type = {}
        total_confidence = 0.0
        
        for record in self.routing_history:
            agent_id = record["agent_id"]
            task_type = record["task_type"]
            
            by_agent[agent_id] = by_agent.get(agent_id, 0) + 1
            by_task_type[task_type] = by_task_type.get(task_type, 0) + 1
            total_confidence += record["confidence"]
        
        return {
            "total_routed": total,
            "by_agent": by_agent,
            "by_task_type": by_task_type,
            "average_confidence": round(total_confidence / total, 2)
        }
    
    def reset_agent_load(self, agent_id: Optional[str] = None):
        """Reset agent load (for testing or when tasks complete)"""
        if agent_id:
            agent_enum = AgentType(agent_id)
            self.agents[agent_enum]["current_load"] = 0
        else:
            for agent in self.agents.values():
                agent["current_load"] = 0