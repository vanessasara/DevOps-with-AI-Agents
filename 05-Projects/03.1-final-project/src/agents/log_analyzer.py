from agents.extensions.models.litellm_model import LitellmModel

from agents import Agent, Runner, set_tracing_disabled

from ..config import Config
from ..tools import get_all_tools

set_tracing_disabled(disabled=True)


class LogAnalyzerAgent:
    """Main Agent - Log Analysis + Kubernetes Operations"""

    def __init__(self):
        self.agent = Agent(
            name="DevOps Incident Responder",
            instructions=Config.get_instructions(),
            model=LitellmModel(
                model=Config.GEMINI_MODEL,
                api_key=Config.GEMINI_API_KEY,
            ),
            tools=get_all_tools(),
        )

    async def process_query(self, user_input: str) -> str:
        # Input Guardrail
        forbidden = ["delete", "drop", "destroy", "format", "password"]
        if any(word in user_input.lower() for word in forbidden):
            return "❌ Guardrail Triggered: Inappropriate or high-risk input detected."

        try:
            result = await Runner.run(self.agent, input=user_input)
            output = getattr(result, "final_output", None)
            output_str = str(output).strip() if output else "No response."

            # Output Guardrail
            if len(output_str) > 2000:
                output_str = output_str[:2000] + "\n...[truncated by guardrail]"

            return output_str
        except Exception as e:
            return f"Error: {e}"


# Summarizer / Orchestrator Agent
class SummarizerAgent:
    """High-level Orchestrator / Dashboard Agent"""

    def __init__(self):
        self.agent = Agent(
            name="Summarizer Agent",
            instructions="""You are the main Summarizer and Orchestrator Agent.
Your job is to provide clean executive summaries of the cluster health, pod status, and incidents.
Coordinate information from tools. Do not execute actions directly — recommend only.""",
            model=LitellmModel(
                model=Config.GEMINI_MODEL,
                api_key=Config.GEMINI_API_KEY,
            ),
            tools=get_all_tools(),
        )

    async def process_query(self, user_input: str) -> str:
        # Input Guardrail
        forbidden = ["delete", "drop", "destroy", "format", "password"]
        if any(word in user_input.lower() for word in forbidden):
            return "❌ Guardrail Triggered: Inappropriate or high-risk input detected."

        try:
            result = await Runner.run(self.agent, input=user_input)
            output = getattr(result, "final_output", None)
            output_str = str(output).strip() if output else "No response."

            # Output Guardrail
            if len(output_str) > 2000:
                output_str = output_str[:2000] + "\n...[truncated by guardrail]"

            return output_str
        except Exception as e:
            return f"Error: {e}"
