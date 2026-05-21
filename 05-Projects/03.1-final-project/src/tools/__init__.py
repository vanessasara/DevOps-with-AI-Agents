"""
Tools package initialization - Combines all tools for the agents
"""

from .k8s_tools import get_k8s_tools
from .log_tools import get_log_tools


def get_all_tools():
    """
    Returns all available tools (Log tools + Kubernetes tools)
    This is used by both LogAnalyzerAgent and SummarizerAgent
    """
    try:
        log_tools = get_log_tools()
        k8s_tools = get_k8s_tools()
        all_tools = log_tools + k8s_tools
        print(
            f"✅ Loaded {len(all_tools)} tools (Log: {len(log_tools)}, K8s: {len(k8s_tools)})"
        )
        return all_tools
    except Exception as e:
        print(f"⚠️ Warning: Error loading tools: {e}")
        return []


# For easy importing
__all__ = ["get_all_tools"]
