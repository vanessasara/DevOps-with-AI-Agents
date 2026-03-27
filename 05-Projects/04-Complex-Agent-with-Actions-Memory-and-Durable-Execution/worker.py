import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from src.config import config
from src.workflows.incident_workflow import IncidentWorkflow

async def main():
    client = await Client.connect(config.TEMPORAL_ADDRESS)
    
    # We will define IncidentWorkflow in the next phase
    worker = Worker(
        client,
        task_queue=config.TASK_QUEUE,
        workflows=[IncidentWorkflow],
        activities=[], # activities will be added later
    )
    
    print(f"Worker started on queue: {config.TASK_QUEUE}")
    await worker.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
