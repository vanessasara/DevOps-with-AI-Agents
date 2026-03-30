from datetime import timedelta
from temporalio import workflow
import asyncio

# Import activities
with workflow.unsafe.imports_passed_through():
    from src.workflows.activities import (
        read_logs_activity,
        analyze_logs_activity,
        slack_notify_activity,
        rds_reboot_activity,
        save_incident_activity
    )

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
        
        # 1. Read logs
        workflow.logger.info("Reading pod logs...")
        logs = await workflow.execute_activity(
            read_logs_activity,
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        # 2. Analyze logs with Agent
        workflow.logger.info("Analyzing logs with AI agent...")
        analysis_result = await workflow.execute_activity(
            analyze_logs_activity,
            args=[logs],
            start_to_close_timeout=timedelta(minutes=2)
        )
        
        analysis_text = analysis_result["analysis"]
        tool_calls = analysis_result["tool_calls"]
        
        # 3. Notify team on Slack
        workflow.logger.info("Sending Slack notification...")
        await workflow.execute_activity(
            slack_notify_activity,
            args=[f"AI Agent Analysis: {analysis_text[:200]}..."],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        # 4. Wait for human approval if tool calls are present
        if tool_calls:
            workflow.logger.info("Destructive action proposed. Waiting for human approval...")
            await self._approved.wait()
            
            if self._is_approved:
                workflow.logger.info("Incident remediation approved")
                
                # Execute tool calls (for now just RDS reboot)
                for tool_call in tool_calls:
                    if tool_call.function.name == "reboot_rds_instance":
                        import json
                        args = json.loads(tool_call.function.arguments)
                        await workflow.execute_activity(
                            rds_reboot_activity,
                            args=[args["instance_id"]],
                            start_to_close_timeout=timedelta(seconds=30)
                        )
                
                # 5. Store incident in pattern memory
                await workflow.execute_activity(
                    save_incident_activity,
                    args=["connection pool exhausted", "rebooted RDS instance"],
                    start_to_close_timeout=timedelta(seconds=10)
                )
                return "Remediation complete: " + analysis_text
            else:
                workflow.logger.info("Incident remediation rejected")
                return "Remediation rejected: " + analysis_text
        else:
            workflow.logger.info("No destructive action proposed. Diagnosis complete.")
            return "Diagnosis complete: " + analysis_text
