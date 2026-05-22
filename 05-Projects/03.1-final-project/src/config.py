import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-2.0-flash")
    FALLBACK_MODELS = os.getenv(
        "FALLBACK_MODELS",
        "groq/llama-3.3-70b-versatile,groq/gemma2-9b-it"
    ).split(",")
    LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "logs")
    K8S_ENABLED = os.getenv("K8S_ENABLED", "false").lower() == "true"
    DOCKER_ENABLED = os.getenv("DOCKER_ENABLED", "true").lower() == "true"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    MCP_ENABLED = os.getenv("MCP_ENABLED", "false").lower() == "true"

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set")
        os.makedirs(cls.LOG_DIRECTORY, exist_ok=True)

    @classmethod
    def get_instructions(cls) -> str:
        p = Path(__file__).parent.parent / "system_prompt.txt"
        return p.read_text(encoding="utf-8") if p.exists() else "You are a DevOps expert."
