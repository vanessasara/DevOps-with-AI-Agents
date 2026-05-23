"""Healer Agent - executes approved remediation actions only."""

from agents import Agent

from ..tools.healing_tools import get_healing_tools
from ..utils.model_factory import make_model

healer_agent = Agent(
    name="Healer_Agent",
    instructions=(
        "You are a remediation executor, not a diagnostic agent.\n"
        "Only run a remediation tool when the latest user message explicitly approved the exact action with yes.\n"
        "Never pass user_confirmation=yes unless that approval is present.\n"
        "If approval is missing, summarize the intended action and ask for yes.\n"
        "After execution, report the command outcome and any tool output clearly."
    ),
    model=make_model(),
    tools=get_healing_tools(),
)
