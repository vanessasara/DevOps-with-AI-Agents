"""Log Analyzer and Kubernetes Agent classes."""

from agents import Agent, Runner, set_tracing_disabled

from ..tools.k8s_tools import get_k8s_tools
from ..utils.model_factory import make_model
from .summarizer_agent import SummarizerAgent
from .triage_agent import triage_agent

set_tracing_disabled(disabled=True)


class LogAnalyzerAgent:
    """Full analysis mode - routes through triage to specialist handoffs."""

    async def process_query(self, user_input: str) -> str:
        try:
            result = await Runner.run(triage_agent, input=user_input)
            return str(getattr(result, "final_output", "") or "").strip() or "No response."
        except Exception as exc:
            return f"Error: {exc}"


class KubernetesAgent:
    """Direct Kubernetes operations - kubectl tools without triage."""

    def _build_agent(self) -> Agent:
        return Agent(
            name="Kubernetes_Agent",
            instructions=(
                "You are a Kubernetes operations expert using kubectl tools only.\n"
                "Start with cluster/pod/event discovery and gather evidence before diagnosing.\n"
                "Quote logs, events, or describe output when giving a conclusion.\n"
                "For restarts, stops, image changes, and resource patches, ask the user to reply yes first.\n"
                "Never pass user_confirmation=yes unless the latest user message explicitly approved that exact action."
            ),
            model=make_model(),
            tools=get_k8s_tools(),
        )

    async def process_query(self, user_input: str) -> str:
        try:
            result = await Runner.run(self._build_agent(), input=user_input)
            return str(getattr(result, "final_output", "") or "").strip() or "No response."
        except Exception as exc:
            return f"Error: {exc}"


__all__ = ["LogAnalyzerAgent", "SummarizerAgent", "KubernetesAgent"]
