from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel
from ..config import Config
from ..tools.github_tools import list_workflow_runs, get_failed_logs, get_workflow_file

def _make_model(model_name: str) -> LitellmModel:
    api_key = Config.GROQ_API_KEY if model_name.startswith("groq/") else Config.GEMINI_API_KEY
    return LitellmModel(model=model_name, api_key=api_key)

github_agent = Agent(
    name="GitHub Specialist",
    instructions="Diagnose GitHub Actions CI/CD failures only. Use only GitHub tools.",
    model=_make_model(Config.GEMINI_MODEL),
    tools=[list_workflow_runs, get_failed_logs, get_workflow_file],
)
