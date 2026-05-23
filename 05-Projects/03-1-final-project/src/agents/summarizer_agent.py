"""Summarizer Agent — high-level orchestrator with full tool access."""

from agents import Agent, Runner, set_tracing_disabled

from ..config import Config
from ..tools import get_all_tools
from ..utils.model_factory import make_model

set_tracing_disabled(disabled=True)

_FORBIDDEN = frozenset(["delete", "drop", "destroy", "format", "password"])
_MAX_CHARS = 2000


class SummarizerAgent:
    def _build_agent(self) -> Agent:
        return Agent(
            name="Summarizer_Agent",
            instructions=Config.get_instructions(),
            model=make_model(),
            tools=get_all_tools(),
        )

    async def process_query(self, user_input: str) -> str:
        if any(w in user_input.lower() for w in _FORBIDDEN):
            return "❌ Guardrail triggered: high-risk input blocked."
        try:
            result = await Runner.run(self._build_agent(), input=user_input)
            output = str(getattr(result, "final_output", "") or "").strip() or "No response."
            if len(output) > _MAX_CHARS:
                output = output[:_MAX_CHARS] + "\n…[truncated]"
            return output
        except Exception as exc:
            return f"❌ Error: {exc}"
