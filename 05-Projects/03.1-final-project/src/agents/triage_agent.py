from agents import Agent, handoff
from agents.extensions.models.litellm_model import LitellmModel
from ..config import Config
from .k8s_agent import k8s_agent
from .docker_agent import docker_agent
from .github_agent import github_agent

def _make_model(model_name: str) -> LitellmModel:
    api_key = Config.GROQ_API_KEY if model_name.startswith("groq/") else Config.GEMINI_API_KEY
    return LitellmModel(model=model_name, api_key=api_key)

triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    You are the first responder. Read the user's question and immediately hand off to the right specialist.
    - Kubernetes / k8s / pod / namespace / OOM / CrashLoop → K8s Specialist
    - Docker / container / docker run → Docker Specialist
    - GitHub / CI / workflow / Actions / pipeline → GitHub Specialist
    Never diagnose yourself. Never use tools yourself. Always hand off immediately.
    """,
    model=_make_model(Config.GEMINI_MODEL),
    handoffs=[handoff(k8s_agent), handoff(docker_agent), handoff(github_agent)],
)
