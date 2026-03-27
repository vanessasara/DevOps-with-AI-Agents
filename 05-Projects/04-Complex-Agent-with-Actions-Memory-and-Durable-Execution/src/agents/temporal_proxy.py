from temporalio.client import Client
from src.config import config

class TemporalClientProxy:
    def __init__(self):
        self.client = None

    async def _get_client(self) -> Client:
        if self.client is None:
            self.client = await Client.connect(config.TEMPORAL_ADDRESS)
        return self.client

    async def start_incident_workflow(self, workflow_id: str):
        client = await self._get_client()
        # IncidentWorkflow name must match the one registered in worker.py
        handle = await client.start_workflow(
            "IncidentWorkflow",
            id=workflow_id,
            task_queue=config.TASK_QUEUE,
        )
        return handle

    async def send_approval_signal(self, workflow_id: str, approved: bool):
        client = await self._get_client()
        handle = client.get_workflow_handle(workflow_id)
        await handle.signal("approval", approved)

    async def get_workflow_status(self, workflow_id: str):
        client = await self._get_client()
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()
        return desc.status

    async def get_workflow_result(self, workflow_id: str):
        client = await self._get_client()
        handle = client.get_workflow_handle(workflow_id)
        return await handle.result()
