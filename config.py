# config.py
import os

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# TranscriptAPI
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY", "")

# YouTube Data API (for basic stats)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Shotstack
SHOTSTACK_API_KEY = os.getenv("SHOTSTACK_API_KEY", "")

# YouTube upload (future)
YOUTUBE_UPLOAD_CLIENT_ID = os.getenv("YOUTUBE_UPLOAD_CLIENT_ID", "")
YOUTUBE_UPLOAD_CLIENT_SECRET = os.getenv("YOUTUBE_UPLOAD_CLIENT_SECRET", "")
YOUTUBE_UPLOAD_REFRESH_TOKEN = os.getenv("YOUTUBE_UPLOAD_REFRESH_TOKEN", "")


def require_env(name: str, value: str):
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")