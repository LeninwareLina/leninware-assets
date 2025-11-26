import os

def require_env(name: str) -> str:
    """
    Fetch an environment variable by name.
    Raises RuntimeError if missing or empty.
    """
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env variable: {name}")
    return value


# --- External API Keys ---
OPENAI_API_KEY = require_env("OPENAI_API_KEY")
ANTHROPIC_API_KEY = require_env("ANTHROPIC_API_KEY")
SHOTSTACK_API_KEY = require_env("SHOTSTACK_API_KEY")
TRANSCRIPT_API_KEY = require_env("TRANSCRIPT_API_KEY")
YOUTUBE_API_KEY = require_env("YOUTUBE_API_KEY")

# --- External URLs ---
TRANSCRIPT_API_URL = "https://transcriptapi.com/v1/transcript"