from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
import asyncio

@workflow.defn
class HealingWorkflow:
    def __init__(self):
        self._approved = False

    @workflow.run
    async def run(self, pod_name: str, namespace: str) -> str:
        logs = await workflow.execute_activity(
            "get_pod_logs",
            args=[pod_name, namespace],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
        diagnosis = await workflow.execute_activity(
            "call_claude_diagnose",
            args=[logs],
            start_to_close_timeout=timedelta(seconds=60),
        )
        # Pause here — wait for user to send approval signal from UI
        await workflow.wait_condition(lambda: self._approved)
        result = await workflow.execute_activity(
            "execute_fix",
            args=[pod_name, namespace, diagnosis],
            start_to_close_timeout=timedelta(seconds=30),
        )
        return result

    @workflow.signal
    def approve(self):
        self._approved = True
