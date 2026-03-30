from typing import Annotated
from pydantic import Field

def send_slack_notification(message: Annotated[str, Field(description="The message to send to the Slack channel")]) -> str:
    """
    Send a notification message to the team's Slack channel.
    
    Use this to alert the team about an incident or a proposed remediation action.
    """
    # Placeholder for real Slack API call
    return f"Slack notification sent: {message} (Simulated)"
