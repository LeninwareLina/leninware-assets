import os
import logging
import requests

logger = logging.getLogger(__name__)

class TranscriptError(Exception):
    pass


def get_transcript(video_url: str) -> str:
    """
    Fetch YouTube transcript using TranscriptAPI.com (v2).
    Returns clean transcript text.
    """

    api_key = os.getenv("TRANSCRIPT_API_KEY")
    if not api_key:
        raise TranscriptError("Missing TRANSCRIPT_API_KEY environment variable.")

    endpoint = "https://transcriptapi.com/api/v2/youtube/transcript"

    params = {
        "video_url": video_url,
        "format": "markdown",          # <<< safer than 'text'
        "include_timestamp": "false",  # keep output clean for Claude
        "send_metadata": "false"       # metadata not needed; avoids extra fields
    }

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=20)
    except Exception as exc:
        raise TranscriptError(f"TranscriptAPI request failed: {exc}")

    if response.status_code != 200:
        raise TranscriptError(
            f"TranscriptAPI HTTP {response.status_code}: {response.text}"
        )

    try:
        data = response.json()
    except Exception:
        raise TranscriptError("TranscriptAPI returned non-JSON response.")

    # 🔥 TEMP DEBUG: print the entire response so we can inspect it
    logger.error("TranscriptAPI RAW RESPONSE: %s", data)

    # The transcript should live inside the "content" field:
    content = data.get("content")

    if not content or not isinstance(content, str):
        raise TranscriptError("TranscriptAPI: response missing 'content' field.")

    return content