"""Central configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini/gemini-2.0-flash")

    LOG_DIRECTORY: str = os.getenv("LOG_DIRECTORY", "logs")
    K8S_ENABLED: bool = os.getenv("K8S_ENABLED", "false").lower() == "true"
    DOCKER_ENABLED: bool = os.getenv("DOCKER_ENABLED", "true").lower() == "true"
    GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")

    MODEL_PROVIDER: str = "Gemini"

    @classmethod
    def validate(cls) -> None:
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env file.")
        os.makedirs(cls.LOG_DIRECTORY, exist_ok=True)

    @classmethod
    def get_instructions(cls) -> str:
        p = Path(__file__).parent.parent / "system_prompt.txt"
        return p.read_text(encoding="utf-8") if p.exists() else "You are a DevOps expert."
