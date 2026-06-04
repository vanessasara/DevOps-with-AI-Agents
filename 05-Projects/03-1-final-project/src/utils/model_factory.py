"""Model factory - OpenRouter-backed Responses model."""

import os

from dotenv import load_dotenv

from agents import AsyncOpenAI, OpenAIResponsesModel, set_tracing_disabled

load_dotenv()
set_tracing_disabled(disabled=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")
BASE_URL = "https://openrouter.ai/api/v1"

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
)


def make_model(model_name: str | None = None) -> OpenAIResponsesModel:
    return OpenAIResponsesModel(
        model=model_name or MODEL,
        openai_client=client,
    )
