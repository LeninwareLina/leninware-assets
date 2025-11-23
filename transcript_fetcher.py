# transcript_fetcher.py
import requests
from config import TRANSCRIPT_API_KEY, require_env

TRANSCRIPT_ENDPOINT = "https://transcriptapi.com/api/v2/youtube/transcript"


def fetch_transcript(video_url: str) -> str:
    """
    Fetches a plain-text transcript using TranscriptAPI.

    Raises RuntimeError on failure.
    """
    require_env("TRANSCRIPT_API_KEY", TRANSCRIPT_API_KEY)

    params = {
        "video_url": video_url,
        "format": "text",
    }
    headers = {
        "Authorization": f"Bearer {TRANSCRIPT_API_KEY}"
    }

    resp = requests.get(TRANSCRIPT_ENDPOINT, params=params, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(
            f"TranscriptAPI error {resp.status_code}: {resp.text}"
        )

    text = resp.text.strip()
    if not text:
        raise RuntimeError("TranscriptAPI returned empty transcript")

    return text