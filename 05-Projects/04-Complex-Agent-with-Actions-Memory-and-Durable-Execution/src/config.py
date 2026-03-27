import os
from pydantic import BaseModel, Field

class Config(BaseModel):
    TEMPORAL_ADDRESS: str = Field(default="localhost:7233")
    TASK_QUEUE: str = Field(default="incident-response-queue")
    K8S_ENABLED: bool = Field(default=False)
    
    # Placeholder for credentials
    ANTHROPIC_API_KEY: str | None = Field(default=None)

    @classmethod
    def load(cls):
        return cls(
            TEMPORAL_ADDRESS=os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
            TASK_QUEUE=os.getenv("TASK_QUEUE", "incident-response-queue"),
            K8S_ENABLED=os.getenv("K8S_ENABLED", "false").lower() == "true",
            ANTHROPIC_API_KEY=os.getenv("ANTHROPIC_API_KEY")
        )

config = Config.load()
