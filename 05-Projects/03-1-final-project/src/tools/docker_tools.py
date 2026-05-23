"""Docker tools - real docker CLI commands on your machine."""

import subprocess

from agents import function_tool

from ..config import Config


def _approved(user_confirmation: str) -> bool:
    return user_confirmation.strip().lower() == "yes"


def _docker(*args: str, timeout: int = 15) -> str:
    """Run a docker command and return combined stdout/stderr."""
    try:
        result = subprocess.run(
            ["docker", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = ((result.stdout or "") + (result.stderr or "")).strip()
        if result.returncode != 0:
            return f"docker exited with code {result.returncode}:\n{output}"
        return output or "docker command completed with no output."
    except FileNotFoundError:
        return "docker not found. Install Docker Desktop or Docker Engine."
    except subprocess.TimeoutExpired:
        return f"docker timed out after {timeout}s."
    except Exception as exc:
        return f"docker error: {exc}"


def _docker_disabled_message(command: str) -> str:
    return (
        f"Blocked real Docker mutation: {command}\n"
        "Set DOCKER_ENABLED=true in .env only when you want approved fixes to run locally."
    )


@function_tool
def list_containers() -> str:
    """List all Docker containers, running and stopped, with their status."""
    return _docker("ps", "-a")


@function_tool
def get_container_logs(container_name: str) -> str:
    """Get the last 100 lines of logs from a Docker container."""
    return _docker("logs", "--tail", "100", container_name, timeout=20)


@function_tool
def inspect_container(container_name: str) -> str:
    """Get detailed container info: state, config, mounts, and network."""
    return _docker("inspect", container_name, timeout=20)


@function_tool
def restart_container(container_name: str, reason: str, user_confirmation: str = "") -> str:
    """Restart a Docker container. Requires user_confirmation exactly yes."""
    if not _approved(user_confirmation):
        return "Blocked: restart_container requires explicit user_confirmation=yes from the user."
    command = f"docker restart {container_name}"
    if not Config.DOCKER_ENABLED:
        return _docker_disabled_message(command)
    result = _docker("restart", container_name, timeout=30)
    return f"Container restart requested.\nReason: {reason}\n{result}"


@function_tool
def stop_container(container_name: str, reason: str, user_confirmation: str = "") -> str:
    """Stop a Docker container. Requires user_confirmation exactly yes."""
    if not _approved(user_confirmation):
        return "Blocked: stop_container requires explicit user_confirmation=yes from the user."
    command = f"docker stop {container_name}"
    if not Config.DOCKER_ENABLED:
        return _docker_disabled_message(command)
    result = _docker("stop", container_name, timeout=30)
    return f"Container stop requested.\nReason: {reason}\n{result}"


def get_docker_tools() -> list:
    return [list_containers, get_container_logs, inspect_container, restart_container, stop_container]
