
import pytest
from orchestrator.advanced_router import TaskRouter, TaskType, AgentType


@pytest.fixture
def router():
    """Create a fresh router instance for each test"""
    return TaskRouter()


@pytest.fixture
def sample_task():
    """Sample task for testing"""
    return {
        "id": "TASK-test123",
        "task_type": "retrieve_records",
        "priority": "high",
        "description": "Retrieve medical records from Dr. Smith",
        "extracted_data": {
            "provider": "Dr. Smith",
            "document_type": "medical_records"
        }
    }


class TestBasicRouting:
    """Test basic routing functionality"""
    
    @pytest.mark.asyncio
    async def test_route_records_task(self, router, sample_task):
        """Test routing a records retrieval task"""
        result = await router.route_task(sample_task)
        
        assert result["agent_id"] == AgentType.RECORDS_WRANGLER.value
        assert result["confidence"] > 0.8
        assert "Records Wrangler" in result["agent_name"]
    
    @pytest.mark.asyncio
    async def test_route_communication_task(self, router):
        """Test routing a client communication task"""
        task = {
            "id": "TASK-comm123",
            "task_type": "client_communication",
            "priority": "medium",
            "description": "Draft response to client inquiry",
            "extracted_data": {}
        }
        
        result = await router.route_task(task)
        
        assert result["agent_id"] == AgentType.COMMUNICATION_GURU.value
        assert result["confidence"] > 0.8
    
    @pytest.mark.asyncio
    async def test_route_legal_research_task(self, router):
        """Test routing a legal research task"""
        task = {
            "id": "TASK-legal123",
            "task_type": "legal_research",
            "priority": "high",
            "description": "Find case law on negligence",
            "extracted_data": {"topic": "negligence"}
        }
        
        result = await router.route_task(task)
        
        assert result["agent_id"] == AgentType.LEGAL_RESEARCHER.value
        assert result["confidence"] > 0.8
    
    @pytest.mark.asyncio
    async def test_route_scheduling_task(self, router):
        """Test routing a scheduling task"""
        task = {
            "id": "TASK-sched123",
            "task_type": "schedule_appointment",
            "priority": "medium",
            "description": "Schedule deposition",
            "extracted_data": {}
        }
        
        result = await router.route_task(task)
        
        assert result["agent_id"] == AgentType.VOICE_SCHEDULER.value
        assert result["confidence"] > 0.8