import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows.heal_workflow import HealingWorkflow
from activities.k8s_activities import get_pod_logs, call_claude_diagnose, execute_fix

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="healing-queue",
        workflows=[HealingWorkflow],
        activities=[get_pod_logs, call_claude_diagnose, execute_fix],
    )
    print("[OK] KubeHealer worker running — Ctrl+C to stop")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
