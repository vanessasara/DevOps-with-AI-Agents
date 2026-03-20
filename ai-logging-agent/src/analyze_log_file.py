import asyncio
import os
from agents import Agent, Runner, set_tracing_disabled, function_tool
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv

load_dotenv()
set_tracing_disabled(disabled=True)

model = "gemini/gemini-3-flash-preview"
api_key = os.environ.get("GEMINI_API_KEY")

@function_tool
def save_summary(summary: str) -> str:
    """Saves the provided summary to Summary.md file."""
    with open('Summary.md', 'w') as f:
        f.write(f"## Summary of the logs\n\n{summary}")
    return "Summary successfully saved to Summary.md"

with open('sample_app.log', 'r') as f:
    logs = f.read()

async def main():
    agent = Agent(
        name="DevOps logs analyzer",
        instructions="""You are an expert DevOps engineer analyzing application logs. 
        After analyzing logs, you MUST call the save_summary tool with your analysis.""",
        model=LitellmModel(model=model, api_key=api_key),
        tools=[save_summary],
    )

    print("Analyzing log file...")
    print("=" * 60)

    result = await Runner.run(
        agent,
        input=f"Analyze the following logs and provide a summary of what happened:\n\n{logs}\n\nThen save the summary using the save_summary tool."
    )

    print(result.final_output)
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())