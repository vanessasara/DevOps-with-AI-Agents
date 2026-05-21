from agents.extensions.models.litellm_model import LitellmModel

from agents import Agent, Runner, set_tracing_disabled

from ..config import Config
from ..tools import get_all_tools

set_tracing_disabled(disabled=True)


class KubernetesAgent:
    """Kubernetes Operations Agent - Specialized in K8s troubleshooting"""

    def __init__(self):
        self.agent = Agent(
            name="Kubernetes Operations Agent",
            instructions="""You are the Kubernetes Operations Agent.
Specialized in inspecting pods, deployments, events, and logs.
You can recommend restarts but must ask for user approval before calling restart tool.
Be detailed and technical when needed.""",
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
