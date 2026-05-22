from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from src.config import Config
from src.agents.triage_agent import triage_agent

set_tracing_disabled(disabled=True)

class LogAnalyzerAgent:
    def __init__(self):
        self.primary_model = Config.GEMINI_MODEL
        self.fallbacks = Config.FALLBACK_MODELS

    async def process_query(self, user_input: str) -> str:
        models_to_try = [self.primary_model] + self.fallbacks
        for model in models_to_try:
            try:
                # Use the triage_agent for the handoff logic
                result = await Runner.run(triage_agent, input=user_input)
                return str(getattr(result, "final_output", "No response.")).strip()
            except Exception as e:
                err = str(e).lower()
                if any(x in err for x in ["429", "quota", "rate limit", "503"]):
                    continue
                return f"Error: {e}"
        return "All models exhausted. Check API keys and quotas."
