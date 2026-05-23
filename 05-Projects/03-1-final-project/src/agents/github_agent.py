"""GitHub Specialist - inspects CI/CD pipelines via gh CLI."""

from agents import Agent

from ..tools.github_tools import get_github_tools
from ..utils.model_factory import make_model

github_agent = Agent(
    name="GitHub_Specialist",
    instructions=(
        "You are a GitHub Actions CI/CD specialist using gh CLI tools only.\n"
        "Start with github_auth_status if authentication is uncertain, then list_workflow_runs.\n"
        "Quote relevant failed step output or check status as evidence.\n"
        "Do not modify repositories, workflows, branches, PRs, issues, or secrets.\n"
        "If gh authentication fails, explain that GITHUB_TOKEN/GH_TOKEN or gh auth login is required."
    ),
    model=make_model(),
    tools=get_github_tools(),
)
