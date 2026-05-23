import os

from dotenv import load_dotenv

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

load_dotenv()
set_tracing_disabled(disabled=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")
base_url = "https://openrouter.ai/api/v1"

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=base_url,
)

agent = Agent(
    name="my agent",
    instructions="You are a helpful assistant",
    model=OpenAIChatCompletionsModel(model=MODEL, openai_client=client),
)

result = Runner.run_sync(starting_agent=agent, input="tell me about DevOps engineering?")
print(result.final_output)
