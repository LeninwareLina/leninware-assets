# config.py
import os


def require_env(name: str) -> str:
    """
    Fetches an environment variable or raises an error.
    """
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value


# === API KEYS ===
OPENAI_API_KEY = require_env("OPENAI_API_KEY")
ANTHROPIC_API_KEY = require_env("ANTHROPIC_API_KEY")
SHOTSTACK_API_KEY = require_env("SHOTSTACK_API_KEY")
TRANSCRIPT_API_KEY = require_env("TRANSCRIPT_API_KEY")
TELEGRAM_BOT_TOKEN = require_env("TELEGRAM_BOT_TOKEN")
YOUTUBE_API_KEY = require_env("YOUTUBE_API_KEY")

# === API BASE URLS ===
TRANSCRIPT_API_URL = "https://api.transcriptapi.com/v1/extract"
SHOTSTACK_BASE_URL = "https://api.shotstack.io/v1/render"