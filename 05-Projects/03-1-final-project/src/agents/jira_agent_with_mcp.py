import argparse
import asyncio
import os

from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

from agents import Agent, Runner
from src.utils.model_factory import make_model

load_dotenv()

params = {
    "command": "uvx",
    "args": [
        "mcp-atlassian",
        f"--jira-url={os.environ['JIRA_URL']}",
        f"--jira-username={os.environ['JIRA_USERNAME']}",
        f"--jira-token={os.environ['JIRA_API_TOKEN']}",
    ],
}


async def run(query: str) -> str:
    async with MCPServerStdio(
        name="jira",
        params=params,
        cache_tools_list=True,
        client_session_timeout_seconds=60,
    ) as server:
        agent = Agent(
            name="jira_agent",
            instructions=(
                "You are a Jira specialist. Use ONLY the MCP tools actually available to you. "
                "NEVER fabricate tool calls or pretend an operation succeeded. "
                "If a tool does not exist in your available tools list, say so explicitly. "
                "Only confirm success after a real tool call returns a result."
            ),
            model=make_model(),
            mcp_servers=[server],
        )
        result = await Runner.run(agent, input=query)
        return str(getattr(result, "final_output", "") or "").strip() or "No response."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Jira agent")
    parser.add_argument("query", nargs="?", default="List all my Jira projects")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    print(await run(args.query))


if __name__ == "__main__":
    asyncio.run(main())
