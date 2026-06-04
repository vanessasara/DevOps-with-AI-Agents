import argparse
import asyncio

from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

from agents import Agent, Runner
from src.utils.model_factory import make_model

load_dotenv()

params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]}


async def run(query: str) -> str:
    async with MCPServerStdio(
        name="github",
        params=params,
        cache_tools_list=True,
        client_session_timeout_seconds=60,
    ) as server:
        agent = Agent(
            name="github_agent",
            instructions=(
                "You are a GitHub specialist. Use GitHub MCP tools to answer questions about "
                "repositories, issues, pull requests, and commits. "
                "Default GitHub user is vanessasara. "
                "If no repo is specified, ask the user to provide owner/repo-name. "
                "Always include links and relevant metadata in responses."
            ),
            model=make_model(),
            mcp_servers=[server],
        )
        result = await Runner.run(agent, input=query)
        return str(getattr(result, "final_output", "") or "").strip() or "No response."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GitHub agent")
    parser.add_argument("query", nargs="?", default="List my GitHub repositories")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    print(await run(args.query))


if __name__ == "__main__":
    asyncio.run(main())
