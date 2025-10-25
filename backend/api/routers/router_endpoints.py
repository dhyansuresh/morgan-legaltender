from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum

from orchestrator.advanced_router import TaskRouter, TaskType, AgentType

router = APIRouter()

# Initialize the router
task_router = TaskRouter()


# Request/Response Models
class TaskInput(BaseModel):
    """Input model for routing a task"""
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task to route")
    priority: str = Field(default="medium", description="Task priority")
    description: str = Field(..., description="Task description")
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "TASK-abc123",
                "task_type": "retrieve_records",
                "priority": "high",
                "description": "Retrieve medical records from Dr. Smith",
                "extracted_data": {
                    "provider": "Dr. Smith",
                    "document_type": "medical_records"
                }
            }
        }


class RoutingResponse(BaseModel):
    """Response model for routing decision"""
    task_id: str
    agent_id: str
    agent_name: str
    confidence: float
    reasoning: str
    estimated_completion_time: int
    agent_specialties: List[str]
    routed_at: str


class BatchTaskInput(BaseModel):
    """Input model for routing multiple tasks"""
    tasks: List[TaskInput]
    consider_load_balancing: bool = Field(
        default=True,
        description="Whether to consider agent load when routing"
    )


class AgentStatusResponse(BaseModel):
    """Response model for agent status"""
    agent_id: str
    name: str
    current_load: int
    max_concurrent_tasks: int
    capacity_percentage: float
    enabled: bool
    success_rate: float


# Endpoints
@router.post("/route", response_model=RoutingResponse, status_code=status.HTTP_200_OK)
async def route_single_task(task: TaskInput):
    """
    Route a single task to the most appropriate AI specialist
    
    This endpoint:
    1. Analyzes the task type and priority
    2. Selects the best agent based on specialties
    3. Considers current agent load
    4. Returns routing decision with confidence score
    """
    try:
        # Convert input to dict for router
        task_dict = {
            "id": task.task_id,
            "task_type": task.task_type,
            "priority": task.priority,
            "description": task.description,
            "extracted_data": task.extracted_data
        }
        
        # Route the task
        routing_decision = await task_router.route_task(task_dict)
        
        return RoutingResponse(
            task_id=task.task_id,
            **routing_decision
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error routing task: {str(e)}"
        )


@router.post("/route/batch", status_code=status.HTTP_200_OK)
async def route_multiple_tasks(batch_input: BatchTaskInput):
    """
    Route multiple tasks at once
    
    Useful when processing a batch of detected tasks from a single message
    """
    try:
        routing_decisions = []
        
        for task in batch_input.tasks:
            task_dict = {
                "id": task.task_id,
                "task_type": task.task_type,
                "priority": task.priority,
                "description": task.description,
                "extracted_data": task.extracted_data
            }
            
            decision = await task_router.route_task(
                task_dict,
                consider_load=batch_input.consider_load_balancing
            )
            
            routing_decisions.append({
                "task_id": task.task_id,
                **decision
            })
        
        return {
            "total_tasks": len(routing_decisions),
            "routing_decisions": routing_decisions,
            "load_balancing_enabled": batch_input.consider_load_balancing
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error routing batch: {str(e)}"
        )


@router.get("/agents/status", status_code=status.HTTP_200_OK)
async def get_all_agents_status():
    """
    Get current status of all AI agents
    
    Shows:
    - Current task load
    - Capacity percentage
    - Success rate
    - Whether agent is enabled
    """
    try:
        status_data = task_router.get_agent_status()
        return {
            "timestamp": "2024-10-25T12:00:00Z",
            "agents": status_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agent status: {str(e)}"
        )


@router.get("/agents/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: str):
    """
    Get status of a specific agent
    """
    try:
        # Validate agent_id
        try:
            AgentType(agent_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found"
            )
        
        status_data = task_router.get_agent_status(agent_id)
        return AgentStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agent status: {str(e)}"
        )


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_routing_statistics():
    """
    Get routing statistics and analytics
    
    Shows:
    - Total tasks routed
    - Distribution by agent
    - Distribution by task type
    - Average confidence scores
    """
    try:
        stats = task_router.get_routing_stats()
        return {
            "statistics": stats,
            "timestamp": "2024-10-25T12:00:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statistics: {str(e)}"
        )


@router.get("/task-types", status_code=status.HTTP_200_OK)
async def get_supported_task_types():
    """
    Get list of all supported task types
    """
    return {
        "task_types": [task_type.value for task_type in TaskType],
        "total": len(TaskType)
    }


@router.get("/agents", status_code=status.HTTP_200_OK)
async def get_available_agents():
    """
    Get list of all available AI agents
    """
    return {
        "agents": [agent_type.value for agent_type in AgentType],
        "total": len(AgentType)
    }


@router.post("/agents/{agent_id}/reset-load", status_code=status.HTTP_200_OK)
async def reset_agent_load(agent_id: str):
    """
    Reset load counter for an agent (for testing/maintenance)
    """
    try:
        # Validate agent_id
        try:
            AgentType(agent_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found"
            )
        
        task_router.reset_agent_load(agent_id)
        
        return {
            "message": f"Load reset for agent '{agent_id}'",
            "agent_id": agent_id,
            "new_load": 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting load: {str(e)}"
        )


@router.post("/reset-all-loads", status_code=status.HTTP_200_OK)
async def reset_all_agent_loads():
    """
    Reset load counters for all agents (for testing/maintenance)
    """
    try:
        task_router.reset_agent_load()
        
        return {
            "message": "All agent loads reset to 0",
            "timestamp": "2024-10-25T12:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting loads: {str(e)}"
        )