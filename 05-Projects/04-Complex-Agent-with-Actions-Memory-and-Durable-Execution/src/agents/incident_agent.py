import litellm
import json
from src.config import config
from src.tools.aws_tools import reboot_rds_instance
from src.tools.slack_tools import send_slack_notification

class IncidentAgent:
    def __init__(self):
        self.system_prompt = self._load_system_prompt()
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "reboot_rds_instance",
                    "description": "Reboot a specified RDS instance. IMPORTANT: Destructive action. Requires human approval.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "instance_id": {
                                "type": "string",
                                "description": "The RDS instance ID to reboot"
                            }
                        },
                        "required": ["instance_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_slack_notification",
                    "description": "Send a notification message to the team's Slack channel.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message to send to Slack"
                            }
                        },
                        "required": ["message"]
                    }
                }
            }
        ]

    def _load_system_prompt(self):
        with open("system_prompt.txt", "r") as f:
            return f.read()

    async def analyze_and_propose(self, log_context: str):
        """
        Analyze logs and propose a remediation action.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Logs:\n{log_context}\nPlease analyze these logs and suggest a remediation."}
        ]
        
        response = await litellm.acompletion(
            model=config.MODEL_NAME,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        
        return response

    async def execute_tool(self, tool_call):
        """
        Execute a tool call from the agent.
        """
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name == "reboot_rds_instance":
            return reboot_rds_instance(**function_args)
        elif function_name == "send_slack_notification":
            return send_slack_notification(**function_args)
        else:
            return f"Error: Tool {function_name} not found."
