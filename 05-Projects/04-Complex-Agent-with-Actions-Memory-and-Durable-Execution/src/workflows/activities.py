import os
import glob
from temporalio import activity
from src.agents.incident_agent import IncidentAgent
from src.memory.pattern_store import PatternStore

@activity.defn
async def read_logs_activity() -> str:
    """
    Read all pod logs from the logs directory.
    """
    log_files = glob.glob("logs/*.log")
    all_logs = ""
    for log_file in log_files:
        with open(log_file, "r") as f:
            all_logs += f"--- {os.path.basename(log_file)} ---\n"
            all_logs += f.read() + "\n"
    return all_logs

@activity.defn
async def analyze_logs_activity(log_context: str) -> dict:
    """
    Agent correlates issues and proposes remediation.
    """
    agent = IncidentAgent()
    store = PatternStore()
    
    # Check memory for similar patterns
    past_context = store.get_context_for_agent("connection pool exhausted")
    combined_context = log_context
    if past_context:
        combined_context = f"{past_context}\n\n{log_context}"
    
    response = await agent.analyze_and_propose(combined_context)
    
    # Extract diagnosis and proposed action
    # For now, we return the full content and any tool calls
    return {
        "analysis": response.choices[0].message.content,
        "tool_calls": response.choices[0].message.tool_calls
    }

@activity.defn
async def slack_notify_activity(message: str) -> str:
    """
    Send alert before action.
    """
    agent = IncidentAgent()
    # We create a dummy tool call to use the existing execute_tool logic
    class DummyToolCall:
        class Function:
            def __init__(self, name, args):
                self.name = name
                self.arguments = args
        def __init__(self, name, args):
            self.function = self.Function(name, args)
            
    import json
    tool_call = DummyToolCall("send_slack_notification", json.dumps({"message": message}))
    return await agent.execute_tool(tool_call)

@activity.defn
async def rds_reboot_activity(instance_id: str) -> str:
    """
    Placeholder RDS reboot.
    """
    agent = IncidentAgent()
    import json
    class DummyToolCall:
        class Function:
            def __init__(self, name, args):
                self.name = name
                self.arguments = args
        def __init__(self, name, args):
            self.function = self.Function(name, args)
            
    tool_call = DummyToolCall("reboot_rds_instance", json.dumps({"instance_id": instance_id}))
    return await agent.execute_tool(tool_call)

@activity.defn
async def save_incident_activity(pattern: str, resolution: str) -> None:
    """
    Store incident in pattern memory.
    """
    store = PatternStore()
    store.save_incident(pattern, resolution)
