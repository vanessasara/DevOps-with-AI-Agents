"""Kubernetes tools - real kubectl commands against the configured cluster."""

import json
import subprocess

from agents import function_tool

from ..config import Config

_ALLOWED_WORKLOADS = {"deployment", "statefulset", "daemonset"}
_ALLOWED_IMAGE_WORKLOADS = {"deployment", "statefulset", "daemonset", "pod"}
_ALLOWED_PATCH_WORKLOADS = {"deployment", "statefulset", "daemonset"}


def _approved(user_confirmation: str) -> bool:
    return user_confirmation.strip().lower() == "yes"


def _kubectl(*args: str, timeout: int = 15) -> str:
    """Run a kubectl command and return combined stdout/stderr."""
    try:
        result = subprocess.run(
            ["kubectl", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = ((result.stdout or "") + (result.stderr or "")).strip()
        if result.returncode != 0:
            return f"kubectl exited with code {result.returncode}:\n{output}"
        return output or "kubectl command completed with no output."
    except FileNotFoundError:
        return "kubectl not found. Install kubectl and configure your kubeconfig."
    except subprocess.TimeoutExpired:
        return f"kubectl timed out after {timeout}s."
    except Exception as exc:
        return f"kubectl error: {exc}"


def _k8s_disabled_message(command: str) -> str:
    return (
        f"Blocked real Kubernetes mutation: {command}\n"
        "Set K8S_ENABLED=true in .env only when you want approved fixes to run against the cluster."
    )


@function_tool
def get_cluster_info() -> str:
    """Show the active Kubernetes context and cluster control-plane information."""
    context = _kubectl("config", "current-context", timeout=10)
    cluster = _kubectl("cluster-info", timeout=15)
    return f"Current context:\n{context}\n\nCluster info:\n{cluster}"


@function_tool
def list_namespaces() -> str:
    """List Kubernetes namespaces visible to the configured kubectl identity."""
    return _kubectl("get", "namespaces", timeout=15)


@function_tool
def list_nodes() -> str:
    """List Kubernetes nodes visible to the configured kubectl identity."""
    return _kubectl("get", "nodes", "-o", "wide", timeout=15)


@function_tool
def list_pods(namespace: str = "default") -> str:
    """List all pods in a Kubernetes namespace with status, restarts, and age."""
    return _kubectl("get", "pods", "-n", namespace, "-o", "wide")


@function_tool
def describe_pod(pod_name: str, namespace: str = "default") -> str:
    """Describe a pod, including events, conditions, resource limits, and image."""
    return _kubectl("describe", "pod", pod_name, "-n", namespace, timeout=20)


@function_tool
def get_pod_logs(pod_name: str, namespace: str = "default", tail: int = 150) -> str:
    """Get the last N lines of logs from a pod."""
    return _kubectl("logs", pod_name, "-n", namespace, "--tail", str(tail), timeout=20)


@function_tool
def get_events(namespace: str = "default") -> str:
    """Get recent warning/error events in a namespace, sorted by timestamp."""
    return _kubectl(
        "get",
        "events",
        "-n",
        namespace,
        "--sort-by=.lastTimestamp",
        "--field-selector",
        "type!=Normal",
    )


@function_tool
def restart_pod(
    pod_name: str,
    namespace: str = "default",
    reason: str = "User requested restart",
    user_confirmation: str = "",
) -> str:
    """Delete a pod so its controller recreates it. Requires user_confirmation exactly yes."""
    if not _approved(user_confirmation):
        return "Blocked: restart_pod requires explicit user_confirmation=yes from the user."
    command = f"kubectl delete pod {pod_name} -n {namespace}"
    if not Config.K8S_ENABLED:
        return _k8s_disabled_message(command)
    result = _kubectl("delete", "pod", pod_name, "-n", namespace, timeout=30)
    return f"Pod restart requested by deleting {pod_name}.\nReason: {reason}\n{result}"


@function_tool
def rollout_restart(
    resource_type: str,
    resource_name: str,
    namespace: str = "default",
    reason: str = "User requested rollout restart",
    user_confirmation: str = "",
) -> str:
    """Restart a Deployment/StatefulSet/DaemonSet rollout. Requires user_confirmation exactly yes."""
    kind = resource_type.lower()
    if kind not in _ALLOWED_WORKLOADS:
        return f"Blocked: resource_type must be one of {sorted(_ALLOWED_WORKLOADS)}."
    if not _approved(user_confirmation):
        return "Blocked: rollout_restart requires explicit user_confirmation=yes from the user."
    command = f"kubectl rollout restart {kind}/{resource_name} -n {namespace}"
    if not Config.K8S_ENABLED:
        return _k8s_disabled_message(command)
    result = _kubectl("rollout", "restart", f"{kind}/{resource_name}", "-n", namespace, timeout=30)
    return f"Rollout restart requested.\nReason: {reason}\n{result}"


@function_tool
def stop_workload(
    resource_type: str,
    resource_name: str,
    namespace: str = "default",
    reason: str = "User requested stop",
    user_confirmation: str = "",
) -> str:
    """Stop a Deployment/StatefulSet by scaling replicas to 0. Requires user_confirmation exactly yes."""
    kind = resource_type.lower()
    if kind not in {"deployment", "statefulset"}:
        return "Blocked: stop_workload only supports deployment or statefulset."
    if not _approved(user_confirmation):
        return "Blocked: stop_workload requires explicit user_confirmation=yes from the user."
    command = f"kubectl scale {kind}/{resource_name} --replicas=0 -n {namespace}"
    if not Config.K8S_ENABLED:
        return _k8s_disabled_message(command)
    result = _kubectl("scale", f"{kind}/{resource_name}", "--replicas=0", "-n", namespace, timeout=30)
    return f"Workload stop requested.\nReason: {reason}\n{result}"


@function_tool
def fix_image(
    resource_type: str,
    resource_name: str,
    namespace: str,
    container_name: str,
    correct_image: str,
    reason: str,
    user_confirmation: str = "",
) -> str:
    """Patch a workload image. Requires user_confirmation exactly yes."""
    kind = resource_type.lower()
    if kind not in _ALLOWED_IMAGE_WORKLOADS:
        return f"Blocked: resource_type must be one of {sorted(_ALLOWED_IMAGE_WORKLOADS)}."
    if not _approved(user_confirmation):
        return "Blocked: fix_image requires explicit user_confirmation=yes from the user."
    command = f"kubectl set image {kind}/{resource_name} {container_name}={correct_image} -n {namespace}"
    if not Config.K8S_ENABLED:
        return _k8s_disabled_message(command)
    result = _kubectl("set", "image", f"{kind}/{resource_name}", f"{container_name}={correct_image}", "-n", namespace, timeout=30)
    return f"Image update requested.\nReason: {reason}\n{result}"


@function_tool
def patch_resources(
    resource_type: str,
    resource_name: str,
    namespace: str,
    container_name: str,
    memory_limit: str,
    reason: str,
    user_confirmation: str = "",
) -> str:
    """Patch memory limits on a workload container. Requires user_confirmation exactly yes."""
    kind = resource_type.lower()
    if kind not in _ALLOWED_PATCH_WORKLOADS:
        return f"Blocked: resource_type must be one of {sorted(_ALLOWED_PATCH_WORKLOADS)}."
    if not _approved(user_confirmation):
        return "Blocked: patch_resources requires explicit user_confirmation=yes from the user."
    patch = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": container_name,
                            "resources": {"limits": {"memory": memory_limit}},
                        }
                    ]
                }
            }
        }
    }
    patch_json = json.dumps(patch)
    command = f"kubectl patch {kind} {resource_name} -n {namespace} --patch <json>"
    if not Config.K8S_ENABLED:
        return _k8s_disabled_message(command) + f"\nPatch: {patch_json}"
    result = _kubectl("patch", kind, resource_name, "-n", namespace, "--patch", patch_json, timeout=30)
    return f"Resource patch requested.\nReason: {reason}\n{result}"


def get_k8s_tools() -> list:
    return [
        get_cluster_info,
        list_namespaces,
        list_nodes,
        list_pods,
        describe_pod,
        get_pod_logs,
        get_events,
        restart_pod,
        rollout_restart,
        stop_workload,
        fix_image,
        patch_resources,
    ]
