import os
from dotenv import load_dotenv

# Load .env locally; on Railway env vars are injected directly
load_dotenv()


def require_env(name: str) -> str:
    """
    Fetch a required environment variable or crash loudly.

    Usage:
        api_key = require_env("OPENAI_API_KEY")
    """
    val = os.getenv(name)
    if not val or val.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


# ---- API ENDPOINT CONSTANTS ----

# TranscriptAPI official v2 endpoint (can be overridden from env)
TRANSCRIPT_API_URL = os.getenv(
    "TRANSCRIPT_API_URL",
    "https://transcriptapi.com/api/v2/youtube/transcript",
)

# YouTube Data API base
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# Shotstack base URL (stage by default, override in Railway if needed)
SHOTSTACK_BASE_URL = os.getenv(
    "SHOTSTACK_BASE_URL",
    "https://api.shotstack.io/stage",
)