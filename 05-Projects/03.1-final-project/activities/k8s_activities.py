from temporalio import activity
import subprocess
from src.config import Config

@activity.defn
async def get_pod_logs(pod_name: str, namespace: str) -> str:
    r = subprocess.run(["kubectl", "logs", pod_name, "-n", namespace], capture_output=True, text=True)
    return r.stdout or r.stderr

@activity.defn
async def call_claude_diagnose(logs: str) -> str:
    # This would call the agent logic; keeping it simple for now as requested
    return f"Diagnosed issue: {logs[:50]}..."

@activity.defn
async def execute_fix(pod_name: str, namespace: str, diagnosis: str) -> str:
    return f"Applied fix to {pod_name} based on: {diagnosis}"
