"""Tools package — aggregates all DevOps tool sets."""
from .docker_tools import get_docker_tools
from .github_tools import get_github_tools
from .healing_tools import get_healing_tools
from .k8s_tools import get_k8s_tools
from .log_tools import get_log_tools


def get_all_tools() -> list:
    """Return every available tool: Log + K8s + Docker + GitHub + Healing."""
    try:
        log = get_log_tools()
        k8s = get_k8s_tools()
        docker = get_docker_tools()
        github = get_github_tools()
        healing = get_healing_tools()
        all_tools = log + k8s + docker + github + healing
        print(
            f"✅ Loaded {len(all_tools)} tools "
            f"(Log: {len(log)}, K8s: {len(k8s)}, Docker: {len(docker)}, "
            f"GitHub: {len(github)}, Healing: {len(healing)})"
        )
        return all_tools
    except Exception as exc:
        print(f"⚠️  Warning: error loading tools: {exc}")
        return []


__all__ = [
    "get_all_tools",
    "get_log_tools", "get_k8s_tools", "get_docker_tools",
    "get_github_tools", "get_healing_tools",
]
