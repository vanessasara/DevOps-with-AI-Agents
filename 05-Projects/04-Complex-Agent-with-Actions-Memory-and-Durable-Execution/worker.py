import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from src.config import config
from src.workflows.incident_workflow import IncidentWorkflow
from src.workflows.activities import (
    read_logs_activity,
    analyze_logs_activity,
    slack_notify_activity,
    rds_reboot_activity,
    save_incident_activity
)

async def main():
    client = await Client.connect(config.TEMPORAL_ADDRESS)
    
    worker = Worker(
        client,
        task_queue=config.TASK_QUEUE,
        workflows=[IncidentWorkflow],
        activities=[
            read_logs_activity,
            analyze_logs_activity,
            slack_notify_activity,
            rds_reboot_activity,
            save_incident_activity
        ],
    )
    
    print(f"Worker started on queue: {config.TASK_QUEUE}")
    await worker.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
