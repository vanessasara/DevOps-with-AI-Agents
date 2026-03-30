import os
from pydantic import BaseModel, Field

class Config(BaseModel):
    TEMPORAL_ADDRESS: str = Field(default="localhost:7233")
    TASK_QUEUE: str = Field(default="incident-response-queue")
    K8S_ENABLED: bool = Field(default=False)
    
    # Credentials
    GEMINI_API_KEY: str | None = Field(default=None)
    OPENAI_API_KEY: str | None = Field(default=None)
    
    # Model configuration
    MODEL_NAME: str = Field(default="gemini/gemini-1.5-flash")

    @classmethod
    def load(cls):
        return cls(
            TEMPORAL_ADDRESS=os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
            TASK_QUEUE=os.getenv("TASK_QUEUE", "incident-response-queue"),
            K8S_ENABLED=os.getenv("K8S_ENABLED", "false").lower() == "true",
            GEMINI_API_KEY=os.getenv("GEMINI_API_KEY"),
            OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
            MODEL_NAME=os.getenv("MODEL_NAME", "gemini/gemini-1.5-flash")
        )

config = Config.load()
