import asyncio
from temporalio.client import Client
from workflows.heal_workflow import HealingWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    handle = await client.start_workflow(
        HealingWorkflow.run,
        args=["my-pod", "default"],
        id="heal-my-pod",
        task_queue="healing-queue",
    )
    print(f"Started workflow: {handle.id}")

if __name__ == "__main__":
    asyncio.run(main())
