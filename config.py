import os
from dotenv import load_dotenv

# -------------------------------------------------
# Load .env file (Railway also injects env vars)
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def require_env(name: str) -> str:
    """Fetch required environment variables or crash loudly."""
    val = os.getenv(name)
    if not val or val.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


# -------------------------------------------------
# API KEYS
# -------------------------------------------------
OPENAI_API_KEY         = require_env("OPENAI_API_KEY")
ANTHROPIC_API_KEY      = os.getenv("ANTHROPIC_API_KEY")          # optional
SHOTSTACK_API_KEY       = os.getenv("SHOTSTACK_API_KEY")         # optional
TELEGRAM_BOT_TOKEN      = os.getenv("TELEGRAM_BOT_TOKEN")         # optional
YOUTUBE_API_KEY         = require_env("YOUTUBE_API_KEY")
TRANSCRIPT_API_KEY      = require_env("TRANSCRIPT_API_KEY")

# -------------------------------------------------
# API ENDPOINTS (CRITICAL — these MUST be exported)
# -------------------------------------------------

# TranscriptAPI official v2 endpoint
TRANSCRIPT_API_URL = os.getenv(
    "TRANSCRIPT_API_URL",
    "https://transcriptapi.com/api/v2/youtube/transcript"
)

# YouTube API
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
# How many videos the ingestor pulls per channel
YOUTUBE_FETCH_LIMIT = int(os.getenv("YOUTUBE_FETCH_LIMIT", "20"))

# Virality scoring threshold
VIRALITY_THRESHOLD = float(os.getenv("VIRALITY_THRESHOLD", "5.0"))