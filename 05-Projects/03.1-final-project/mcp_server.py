"""
MCP Server — exposes all DevOps tools via Model Context Protocol.
Works with Claude Desktop, VS Code, Cursor, any MCP client.
Run: uv run python mcp_server.py
"""
import subprocess
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("DevOps Tools")

@mcp.tool
def list_pods(namespace: str = "default") -> str:
    """List all pods in a Kubernetes namespace."""
    r = subprocess.run(["kubectl", "get", "pods", "-n", namespace], capture_output=True, text=True)
    return r.stdout or r.stderr

@mcp.tool
def describe_pod(pod_name: str, namespace: str = "default") -> str:
    """Describe a Kubernetes pod including events."""
    r = subprocess.run(["kubectl", "describe", "pod", pod_name, "-n", namespace], capture_output=True, text=True)
    return r.stdout or r.stderr

@mcp.tool
def get_k8s_events(namespace: str = "default") -> str:
    """Get recent Kubernetes events sorted by timestamp."""
    r = subprocess.run(["kubectl", "get", "events", "-n", namespace, "--sort-by=.lastTimestamp"], capture_output=True, text=True)
    return r.stdout or r.stderr

@mcp.tool
def list_containers() -> str:
    """List all Docker containers."""
    r = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
    return r.stdout or r.stderr

@mcp.tool
def get_container_logs(container_name: str) -> str:
    """Get logs from a Docker container."""
    r = subprocess.run(["docker", "logs", "--tail", "100", container_name], capture_output=True, text=True)
    return r.stdout + r.stderr

@mcp.tool
def list_workflow_runs(status: str = "failure") -> str:
    """List recent GitHub Actions workflow runs."""
    r = subprocess.run(["gh", "run", "list", "--status", status, "--limit", "5"], capture_output=True, text=True)
    return r.stdout or r.stderr

if __name__ == "__main__":
    mcp.run()
