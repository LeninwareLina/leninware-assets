# config.py

import os


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


# ========== API KEYS ==========
OPENAI_API_KEY = require_env("OPENAI_API_KEY")
YOUTUBE_API_KEY = require_env("YOUTUBE_API_KEY")
SHOTSTACK_API_KEY = require_env("SHOTSTACK_API_KEY")
TRANSCRIPT_API_KEY = require_env("TRANSCRIPT_API_KEY")


# ========== TRANSCRIPT API ==========
# You specifically requested transcriptapi.com instead of api.transcriptapi.com
TRANSCRIPT_API_BASE_URL = "https://transcriptapi.com"

# Adjusted to use the correct YouTube endpoint for TranscriptAPI v2
TRANSCRIPT_API_V2_URL = f"{TRANSCRIPT_API_BASE_URL}/api/v2/youtube"


# ========== SHOTSTACK ==========
SHOTSTACK_API_URL = "https://api.shotstack.io/v1/render"


# ========== YOUTUBE UPLOAD ==========
YOUTUBE_CLIENT_ID = require_env("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = require_env("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = require_env("YOUTUBE_REFRESH_TOKEN")