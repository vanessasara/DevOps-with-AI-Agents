import argparse
import asyncio

from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

from agents import Agent, Runner
from src.utils.model_factory import make_model

load_dotenv()

params = {"command": "uvx", "args": ["mcp-server-time"]}


async def run(query: str) -> str:
    async with MCPServerStdio(
        name="time",
        params=params,
        cache_tools_list=True,
        client_session_timeout_seconds=60,
    ) as server:
        agent = Agent(
            name="time_agent",
            instructions=(
                "You are a time assistant. Use get_current_time and convert_time tools. "
                "Default timezone is Asia/Karachi if none is specified. "
                "Keep responses concise and include the timezone used."
            ),
            model=make_model(),
            mcp_servers=[server],
        )
        result = await Runner.run(agent, input=query)
        return str(getattr(result, "final_output", "") or "").strip() or "No response."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Time agent")
    parser.add_argument("query", nargs="?", default="What time is it in Asia/Karachi?")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    print(await run(args.query))


if __name__ == "__main__":
    asyncio.run(main())
