import os


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


# ----------------------------------------
#   GLOBAL MOCK FLAG
# ----------------------------------------
USE_MOCK_AI = os.getenv("USE_MOCK_AI", "false").lower() == "true"


# ----------------------------------------
#   OpenAI
# ----------------------------------------
if USE_MOCK_AI:
    OPENAI_API_KEY = "mock"
else:
    OPENAI_API_KEY = require_env("OPENAI_API_KEY")


# ----------------------------------------
#   TranscriptAPI
# ----------------------------------------
if USE_MOCK_AI:
    TRANSCRIPT_API_KEY = "mock"
else:
    TRANSCRIPT_API_KEY = require_env("TRANSCRIPT_API_KEY")

TRANSCRIPT_API_BASE_URL = "https://transcriptapi.com"
TRANSCRIPT_API_V2_URL = f"{TRANSCRIPT_API_BASE_URL}/api/v2/youtube"


# ----------------------------------------
#   YouTube Ingest
# ----------------------------------------
if USE_MOCK_AI:
    YOUTUBE_API_KEY = "mock"
else:
    YOUTUBE_API_KEY = require_env("YOUTUBE_API_KEY")


# ----------------------------------------
#   YouTube Upload OAuth
# ----------------------------------------
if USE_MOCK_AI:
    YOUTUBE_CLIENT_ID = "mock"
    YOUTUBE_CLIENT_SECRET = "mock"
    YOUTUBE_REFRESH_TOKEN = "mock"
else:
    YOUTUBE_CLIENT_ID = require_env("GOOGLE_CLIENT_ID")
    YOUTUBE_CLIENT_SECRET = require_env("GOOGLE_CLIENT_SECRET")
    YOUTUBE_REFRESH_TOKEN = require_env("GOOGLE_REFRESH_TOKEN")


# ----------------------------------------
#   Shotstack
# ----------------------------------------
if USE_MOCK_AI:
    SHOTSTACK_API_KEY = "mock"
else:
    SHOTSTACK_API_KEY = require_env("SHOTSTACK_API_KEY")

SHOTSTACK_API_URL = "https://api.shotstack.io/v1/render"