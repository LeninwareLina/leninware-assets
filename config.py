# config.py
import os
from dotenv import load_dotenv

load_dotenv()


def require_env(name: str, default: str | None = None) -> str:
    """
    Ensure an environment variable is set.
    Optionally allow a default.
    """
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# Core services
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")
TRANSCRIPT_API_URL = os.getenv(
    "TRANSCRIPT_API_URL",
    "https://transcriptapi.com/api/v2/youtube/transcript",
)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Shotstack / rendering
SHOTSTACK_API_KEY = os.getenv("SHOTSTACK_API_KEY")
SHOTSTACK_BASE_URL = os.getenv(
    "SHOTSTACK_BASE_URL",
    "https://api.shotstack.io/stage/render",
)

# Runtime
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")