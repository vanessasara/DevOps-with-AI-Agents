import pytest
import os
import json
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.incident_agent import IncidentAgent
from src.memory.pattern_store import PatternStore
from src.workflows.activities import analyze_logs_activity

@pytest.fixture
def temp_db():
    db_path = "data/test_pattern_memory.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_agent_analyze_and_propose():
    agent = IncidentAgent()
    log_context = "connection pool exhausted"
    
    with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Reboot RDS"
        
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "reboot_rds_instance"
        mock_tool_call.function.arguments = '{"instance_id": "prod-db"}'
        
        mock_message.tool_calls = [mock_tool_call]
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_completion.return_value = mock_response
        
        response = await agent.analyze_and_propose(log_context)
        assert response.choices[0].message.content == "Reboot RDS"
        assert response.choices[0].message.tool_calls[0].function.name == "reboot_rds_instance"

def test_pattern_store(temp_db):
    store = PatternStore(db_path=temp_db)
    store.save_incident("connection pool exhausted", "rebooted RDS instance")
    
    context = store.get_context_for_agent("connection")
    assert "connection pool exhausted" in context
    assert "rebooted RDS instance" in context

@pytest.mark.asyncio
async def test_analyze_logs_activity():
    log_context = "Error: connection pool exhausted"
    
    with patch("src.agents.incident_agent.IncidentAgent.analyze_and_propose", new_callable=AsyncMock) as mock_analyze:
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Analyze result"
        mock_message.tool_calls = []
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_analyze.return_value = mock_response
        
        # We need to mock PatternStore in the activity
        with patch("src.workflows.activities.PatternStore") as MockStore:
            MockStore.return_value.get_context_for_agent.return_value = ""
            
            result = await analyze_logs_activity(log_context)
            assert result["analysis"] == "Analyze result"
            assert result["tool_calls"] == []
