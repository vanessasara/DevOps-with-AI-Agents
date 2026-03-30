from typing import Annotated
from pydantic import Field

def reboot_rds_instance(instance_id: Annotated[str, Field(description="The RDS instance ID to reboot")]) -> str:
    """
    Reboot a specified RDS instance.
    
    IMPORTANT: This is a destructive action.
    DO NOT call this tool unless the engineer has explicitly typed 'yes' in response to a proposal.
    """
    # Placeholder for real AWS SDK call
    return f"Successfully rebooted RDS instance: {instance_id} (Simulated)"
