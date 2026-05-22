from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel
from ..config import Config
from ..tools.docker_tools import list_containers, get_container_logs, inspect_container, restart_container

def _make_model(model_name: str) -> LitellmModel:
    api_key = Config.GROQ_API_KEY if model_name.startswith("groq/") else Config.GEMINI_API_KEY
    return LitellmModel(model=model_name, api_key=api_key)

docker_agent = Agent(
    name="Docker Specialist",
    instructions="Diagnose Docker issues only. Use only Docker tools. Never call K8s or GitHub tools.",
    model=_make_model(Config.GEMINI_MODEL),
    tools=[list_containers, get_container_logs, inspect_container, restart_container],
)
