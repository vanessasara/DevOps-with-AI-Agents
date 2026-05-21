import subprocess

from agents import function_tool

from ..config import Config

# ========================
# Kubernetes Operations Agent Tools
# ========================


@function_tool
def list_pods(namespace: str = "default") -> str:
    """List all pods in a namespace with status and age."""
    cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "wide"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Error listing pods: {e}"


@function_tool
def describe_pod(pod_name: str, namespace: str = "default") -> str:
    """Describe a specific pod (includes events and conditions)."""
    cmd = ["kubectl", "describe", "pod", pod_name, "-n", namespace]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Error describing pod: {e}"


@function_tool
def get_pod_logs(pod_name: str, namespace: str = "default", tail: int = 150) -> str:
    """Get recent logs from a pod."""
    cmd = ["kubectl", "logs", pod_name, "-n", namespace, "--tail", str(tail)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Error getting logs: {e}"


@function_tool
def get_events(namespace: str = "default") -> str:
    """Get recent events in the namespace."""
    cmd = [
        "kubectl",
        "get",
        "events",
        "-n",
        namespace,
        "--sort-by=.lastTimestamp",
        "--field-selector",
        "type!=Normal",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Error getting events: {e}"


@function_tool
def restart_kubernetes_pod(
    pod_name: str, namespace: str = "default", reason: str = "User requested restart"
) -> str:
    """Restart a Kubernetes pod by deleting it (Deployment will recreate it).
    ALWAYS get explicit user approval before calling this tool."""

    if not Config.K8S_ENABLED:
        return f"[SIMULATION MODE] Pod '{pod_name}' in namespace '{namespace}' would be restarted.\nReason: {reason}"

    try:
        result = subprocess.run(
            ["kubectl", "delete", "pod", pod_name, "-n", namespace],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return f"✅ Successfully restarted pod '{pod_name}' in namespace '{namespace}'.\nReason: {reason}"
        else:
            return f"❌ Failed to restart pod: {result.stderr}"
    except Exception as e:
        return f"Error restarting pod: {e}"


def get_k8s_tools():
    return [list_pods, describe_pod, get_pod_logs, get_events, restart_kubernetes_pod]
