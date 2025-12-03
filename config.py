# config.py

import os


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


# -------------------------
#   OpenAI
# -------------------------
OPENAI_API_KEY = require_env("OPENAI_API_KEY")


# -------------------------
#   TranscriptAPI
# -------------------------
TRANSCRIPT_API_KEY = require_env("TRANSCRIPT_API_KEY")
TRANSCRIPT_API_BASE_URL = "https://transcriptapi.com"
TRANSCRIPT_API_V2_URL = f"{TRANSCRIPT_API_BASE_URL}/api/v2/youtube"


# -------------------------
#   YouTube Ingest (only needs API key)
# -------------------------
YOUTUBE_API_KEY = require_env("YOUTUBE_API_KEY")


# -------------------------
#   YouTube Upload (Railway names)
#   NOTE: Railway uses GOOGLE_* names.
#   We map them directly here.
# -------------------------
YOUTUBE_CLIENT_ID = require_env("GOOGLE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = require_env("GOOGLE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = require_env("GOOGLE_REFRESH_TOKEN")


# -------------------------
#   Shotstack
# -------------------------
SHOTSTACK_API_KEY = require_env("SHOTSTACK_API_KEY")
SHOTSTACK_API_URL = "https://api.shotstack.io/v1/render"