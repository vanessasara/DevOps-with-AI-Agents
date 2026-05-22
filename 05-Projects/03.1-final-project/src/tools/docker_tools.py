import subprocess
from agents import function_tool
from src.config import Config

@function_tool
def list_containers() -> str:
    """List all Docker containers (running and stopped) with their status."""
    r = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
    return r.stdout or r.stderr

@function_tool
def get_container_logs(container_name: str) -> str:
    """Get the last 100 lines of logs from a Docker container."""
    r = subprocess.run(
        ["docker", "logs", "--tail", "100", container_name],
        capture_output=True, text=True
    )
    return r.stdout + r.stderr

@function_tool
def inspect_container(container_name: str) -> str:
    """Get detailed info about a Docker container: state, config, mounts, network."""
    r = subprocess.run(
        ["docker", "inspect", container_name],
        capture_output=True, text=True
    )
    return r.stdout or r.stderr

@function_tool
def restart_container(container_name: str, reason: str) -> str:
    """Restart a Docker container. ALWAYS get explicit user approval before calling.
    Never call this without the user saying yes."""
    if not Config.DOCKER_ENABLED:
        return f"[SIMULATED] docker restart {container_name}\nReason: {reason}"
    r = subprocess.run(
        ["docker", "restart", container_name],
        capture_output=True, text=True
    )
    return r.stdout or r.stderr


def get_docker_tools():
    return [list_containers, get_container_logs, inspect_container, restart_container]

