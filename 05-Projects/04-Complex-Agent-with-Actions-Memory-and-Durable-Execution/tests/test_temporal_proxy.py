import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from src.agents.temporal_proxy import TemporalClientProxy

@pytest.mark.asyncio
async def test_start_incident_workflow():
    proxy = TemporalClientProxy()
    # Mocking Temporal Client
    proxy.client = AsyncMock()
    
    workflow_id = "test-workflow"
    await proxy.start_incident_workflow(workflow_id)
    
    proxy.client.start_workflow.assert_called_once()

@pytest.mark.asyncio
async def test_send_approval_signal():
    proxy = TemporalClientProxy()
    # Mocking Temporal Client
    proxy.client = AsyncMock()
    
    workflow_id = "test-workflow"
    await proxy.send_approval_signal(workflow_id, True)
    
    proxy.client.get_workflow_handle.assert_called_with(workflow_id)
    proxy.client.get_workflow_handle.return_value.signal.assert_called_with("approval", True)
