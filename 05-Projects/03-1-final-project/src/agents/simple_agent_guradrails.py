import os

from dotenv import load_dotenv
from pydantic import BaseModel

from agents import (
    Agent,
    AsyncOpenAI,
    GuardrailFunctionOutput,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
)

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

model = OpenAIChatCompletionsModel(model=MODEL, openai_client=client)


# ── Input guardrail — block destructive DevOps commands ───────────────────────


class DestructiveCommandOutput(BaseModel):
    is_destructive: bool
    reasoning: str


input_guardrail_agent = Agent(
    name="Input_Guardrail_Check",
    instructions=(
        "Check if the user is asking to execute a destructive or irreversible DevOps command "
        "such as deleting namespaces, dropping databases, wiping disks, force-deleting pods, "
        "or any action that could cause data loss or a service outage without a rollback plan."
    ),
    model=model,
    output_type=DestructiveCommandOutput,
)


@input_guardrail
async def destructive_command_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(input_guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_destructive,
    )


# ── Output guardrail — block responses that expose secrets ────────────────────


class ExposedSecretsOutput(BaseModel):
    contains_secrets: bool
    reasoning: str


output_guardrail_agent = Agent(
    name="Output_Guardrail_Check",
    instructions=(
        "Check if the response contains sensitive secrets or credentials such as "
        "API keys, passwords, tokens, private keys, connection strings, or any value "
        "that looks like a secret that should not be exposed to the user."
    ),
    model=model,
    output_type=ExposedSecretsOutput,
)


@output_guardrail
async def secrets_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:
    result = await Runner.run(output_guardrail_agent, output, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.contains_secrets,
    )
