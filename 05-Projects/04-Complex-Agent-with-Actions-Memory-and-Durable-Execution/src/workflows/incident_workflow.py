from temporalio import workflow
import asyncio

@workflow.defn
class IncidentWorkflow:
    def __init__(self) -> None:
        self._approved = asyncio.Event()
        self._is_approved = False

    @workflow.signal
    def approval(self, approved: bool) -> None:
        self._is_approved = approved
        self._approved.set()

    @workflow.run
    async def run(self) -> str:
        workflow.logger.info("Incident diagnosis workflow started")
        
        # Wait for human approval signal
        workflow.logger.info("Waiting for human approval...")
        await self._approved.wait()
        
        if self._is_approved:
            workflow.logger.info("Incident remediation approved")
            return "Remediation complete"
        else:
            workflow.logger.info("Incident remediation rejected")
            return "Remediation rejected"
