"""Healing tools - approved remediation actions only."""

import json
import subprocess

from agents import function_tool

from ..config import Config

_ALLOWED_IMAGE_WORKLOADS = {"deployment", "statefulset", "daemonset", "pod"}
_ALLOWED_PATCH_WORKLOADS = {"deployment", "statefulset", "daemonset"}


def _approved(user_confirmation: str) -> bool:
    return user_confirmation.strip().lower() == "yes"


def _kubectl(*args: str, timeout: int = 30) -> str:
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
def heal_fix_image(
    resource_type: str,
    resource_name: str,
    namespace: str,
    container_name: str,
    correct_image: str,
    reason: str,
    user_confirmation: str = "",
) -> str:
    """Patch a Kubernetes resource image. Requires user_confirmation exactly yes."""
    kind = resource_type.lower()
    if kind not in _ALLOWED_IMAGE_WORKLOADS:
        return f"Blocked: resource_type must be one of {sorted(_ALLOWED_IMAGE_WORKLOADS)}."
    if not _approved(user_confirmation):
        return "Blocked: heal_fix_image requires explicit user_confirmation=yes from the user."
    command = f"kubectl set image {kind}/{resource_name} {container_name}={correct_image} -n {namespace}"
    if not Config.K8S_ENABLED:
        return _k8s_disabled_message(command)
    result = _kubectl("set", "image", f"{kind}/{resource_name}", f"{container_name}={correct_image}", "-n", namespace)
    return f"Image update requested.\nReason: {reason}\n{result}"


@function_tool
def heal_patch_resources(
    resource_type: str,
    resource_name: str,
    namespace: str,
    container_name: str,
    memory_limit: str,
    reason: str,
    user_confirmation: str = "",
) -> str:
    """Patch memory limits on a Kubernetes workload. Requires user_confirmation exactly yes."""
    kind = resource_type.lower()
    if kind not in _ALLOWED_PATCH_WORKLOADS:
        return f"Blocked: resource_type must be one of {sorted(_ALLOWED_PATCH_WORKLOADS)}."
    if not _approved(user_confirmation):
        return "Blocked: heal_patch_resources requires explicit user_confirmation=yes from the user."
    patch_json = json.dumps({
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
    })
    command = f"kubectl patch {kind} {resource_name} -n {namespace} --patch <json>"
    if not Config.K8S_ENABLED:
        return _k8s_disabled_message(command) + f"\nPatch: {patch_json}"
    result = _kubectl("patch", kind, resource_name, "-n", namespace, "--patch", patch_json)
    return f"Resource patch requested.\nReason: {reason}\n{result}"


@function_tool
def cache_clear(service_name: str, reason: str, user_confirmation: str = "") -> str:
    """Simulate clearing application cache for a service. Requires user_confirmation exactly yes."""
    if not _approved(user_confirmation):
        return "Blocked: cache_clear requires explicit user_confirmation=yes from the user."
    return f"[SIMULATED] Cache cleared for {service_name}.\nReason: {reason}"


@function_tool
def disk_cleanup(path: str, reason: str, user_confirmation: str = "") -> str:
    """Simulate disk cleanup at a path. Requires user_confirmation exactly yes."""
    if not _approved(user_confirmation):
        return "Blocked: disk_cleanup requires explicit user_confirmation=yes from the user."
    return f"[SIMULATED] Disk cleanup at {path}.\nReason: {reason}"


def get_healing_tools() -> list:
    return [heal_fix_image, heal_patch_resources, cache_clear, disk_cleanup]
