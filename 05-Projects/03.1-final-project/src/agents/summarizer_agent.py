from agents.extensions.models.litellm_model import LitellmModel

from agents import Agent, Runner, set_tracing_disabled

from ..config import Config
from ..tools import get_all_tools

set_tracing_disabled(disabled=True)


class SummarizerAgent:
    """Main Orchestrator / Summarizer Agent (High-level Dashboard)"""

    def __init__(self):
        self.agent = Agent(
            name="Summarizer Agent",
            instructions="""You are the **Summarizer Agent** — the main orchestrator of the DevOps platform.

Your responsibilities:
- Provide clean, executive-level summaries of the entire infrastructure
- Cover Kubernetes cluster health, pod status, deployments, and recent incidents
- Aggregate information from logs, events, and tools
- Give clear recommended actions
- Do NOT perform actions yourself (only recommend)

Always structure your response with:
1. Overall Status
2. Key Issues (with severity)
3. Recommended Actions
4. Summary

Be concise and professional.""",
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
            
            # Extract usage if available
            usage = getattr(result, "usage", {})
            
            output = getattr(result, "final_output", None)
            output_str = str(output).strip() if output else "No response."

            # Output Guardrail
            if len(output_str) > 2000:
                output_str = output_str[:2000] + "\n...[truncated by guardrail]"

            return output_str
        except Exception as e:
            return f"Error: {e}"
