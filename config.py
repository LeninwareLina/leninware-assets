# config.py
import os


def require_env(name: str) -> str:
    """
    Fetch an environment variable or raise an error if missing.
    Used for sensitive configuration like API keys.
    """
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value


# Base URLs for external services. These are stable constants and do NOT
# attempt to read secrets at import time.
TRANSCRIPT_API_BASE_URL = "https://api.transcriptapi.com"
TRANSCRIPT_API_V2_URL = f"{TRANSCRIPT_API_BASE_URL}/api/v2/video-transcript"

SHOTSTACK_API_URL = "https://api.shotstack.io/edit/v1/render"