"""Model factory - single OpenRouter chat completions model."""

import os

from dotenv import load_dotenv

from agents import AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

load_dotenv()
set_tracing_disabled(disabled=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")
BASE_URL = "https://openrouter.ai/api/v1"

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
)


def make_model(model_name: str | None = None) -> OpenAIChatCompletionsModel:
    return OpenAIChatCompletionsModel(
        model=MODEL,
        openai_client=client,
    )
