"""Triage Agent - first responder that routes queries to the right specialist."""

from agents import Agent, handoff

from ..utils.model_factory import make_model
from .docker_agent import docker_agent
from .github_agent import github_agent
from .healer_agent import healer_agent
from .k8s_agent import k8s_agent

triage_agent = Agent(
    name="Triage_Agent",
    instructions=(
        "You are the incident first responder and router. Do not use tools.\n"
        "Hand off to exactly one specialist when the target domain is clear.\n"
        "Kubernetes/k8s/pod/namespace/OOMKilled/CrashLoopBackOff/restart pod/stop workload -> K8s_Specialist.\n"
        "Docker/container/image/docker restart/docker stop -> Docker_Specialist.\n"
        "GitHub/CI/workflow/Actions/pipeline/PR -> GitHub_Specialist.\n"
        "Approved remediation after a prior diagnosis -> Healer_Agent.\n"
        "If ambiguous, ask one clarifying question. Never diagnose without specialist evidence.\n"
        "Never claim an action was taken; only the specialist or healer tools can do that."
    ),
    model=make_model(),
    handoffs=[
        handoff(k8s_agent),
        handoff(docker_agent),
        handoff(github_agent),
        handoff(healer_agent),
    ],
)
