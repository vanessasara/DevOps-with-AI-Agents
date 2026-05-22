from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel
from ..config import Config
from ..tools.healing_tools import cache_clear, disk_cleanup

def _make_model(model_name: str) -> LitellmModel:
    api_key = Config.GROQ_API_KEY if model_name.startswith("groq/") else Config.GEMINI_API_KEY
    return LitellmModel(model=model_name, api_key=api_key)

healer_agent = Agent(
    name="Healer Agent",
    instructions="Execute approved fixes only. No analysis tools.",
    model=_make_model(Config.GEMINI_MODEL),
    tools=[cache_clear, disk_cleanup],
)
