"""
Tools package initialization - Combines all tools for the agents
"""

from .k8s_tools import get_k8s_tools
from .log_tools import get_log_tools
from .docker_tools import get_docker_tools
from .github_tools import get_github_tools
from .healing_tools import get_healing_tools


def get_all_tools():
    """
    Returns all available tools (Log, K8s, Docker, GitHub, Healing)
    """
    try:
        log_tools = get_log_tools()
        k8s_tools = get_k8s_tools()
        docker_tools = get_docker_tools()
        github_tools = get_github_tools()
        healing_tools = get_healing_tools()
        
        all_tools = log_tools + k8s_tools + docker_tools + github_tools + healing_tools
        
        print(
            f"✅ Loaded {len(all_tools)} tools (Log: {len(log_tools)}, K8s: {len(k8s_tools)}, "
            f"Docker: {len(docker_tools)}, GitHub: {len(github_tools)}, Healing: {len(healing_tools)})"
        )
        return all_tools
    except Exception as e:
        print(f"⚠️ Warning: Error loading tools: {e}")
        return []


# For easy importing
__all__ = ["get_all_tools"]
