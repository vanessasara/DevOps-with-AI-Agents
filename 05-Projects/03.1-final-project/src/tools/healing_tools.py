import subprocess
from agents import function_tool
from src.config import Config

@function_tool
def fix_image(resource_type: str, resource_name: str, namespace: str, correct_image: str, reason: str) -> str:
    """Patch a Kubernetes resource to fix a wrong container image.
    ALWAYS get explicit user approval before calling."""
    if not Config.K8S_ENABLED:
        return f"[SIMULATED] kubectl set image {resource_type}/{resource_name} app={correct_image} -n {namespace}
Reason: {reason}"
    r = subprocess.run(
        ["kubectl", "set", "image", f"{resource_type}/{resource_name}",
         f"app={correct_image}", "-n", namespace],
        capture_output=True, text=True
    )
    return r.stdout or r.stderr

@function_tool
def patch_resources(resource_type: str, resource_name: str, namespace: str, memory_limit: str, reason: str) -> str:
    """Patch memory limits on a Kubernetes resource.
    ALWAYS get explicit user approval before calling."""
    patch = f'{{"spec":{{"template":{{"spec":{{"containers":[{{"name":"app","resources":{{"limits":{{"memory":"{memory_limit}"}}}}}}]}}}}}}}}'
    if not Config.K8S_ENABLED:
        return f"[SIMULATED] kubectl patch {resource_type} {resource_name} -n {namespace}
Patch: {patch}
Reason: {reason}"
    r = subprocess.run(
        ["kubectl", "patch", resource_type, resource_name, "-n", namespace,
         "--patch", patch],
        capture_output=True, text=True
    )
    return r.stdout or r.stderr

@function_tool
def cache_clear(service_name: str, reason: str) -> str:
    """Simulate clearing application cache for a service.
    ALWAYS get explicit user approval before calling."""
    return f"[SIMULATED] Cache cleared for {service_name}.
Reason: {reason}"

@function_tool
def disk_cleanup(path: str, reason: str) -> str:
    """Simulate disk cleanup at a path.
    ALWAYS get explicit user approval before calling."""
    return f"[SIMULATED] Disk cleanup at {path}.\nReason: {reason}"


def get_healing_tools():
    return [fix_image, patch_resources, cache_clear, disk_cleanup]

