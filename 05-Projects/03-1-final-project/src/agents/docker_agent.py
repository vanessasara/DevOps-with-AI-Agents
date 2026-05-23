"""Docker Specialist - inspects and manages containers via docker CLI."""

from agents import Agent

from ..tools.docker_tools import get_docker_tools
from ..utils.model_factory import make_model

docker_agent = Agent(
    name="Docker_Specialist",
    instructions=(
        "You are a Docker specialist using docker CLI tools only.\n"
        "Always call list_containers before inspecting or diagnosing a container.\n"
        "Quote evidence from container status, logs, or inspect output.\n"
        "For restart_container or stop_container, first explain the action and ask the user to reply yes.\n"
        "Never pass user_confirmation=yes unless the latest user message explicitly approved that exact action.\n"
        "Never invent container names or causes not present in tool output."
    ),
    model=make_model(),
    tools=get_docker_tools(),
)
