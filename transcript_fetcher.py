import requests
from config import require_env, TRANSCRIPT_API_URL

def fetch_transcript(video_url: str) -> str:
    if not video_url:
        raise ValueError("fetch_transcript() called with empty video_url")

    api_key = require_env("TRANSCRIPT_API_KEY")

    headers = {
        "X-API-Key": api_key,    # this capitalization matters!
        "Accept": "text/plain",
    }

    params = {
        "video_url": video_url
    }

    try:
        resp = requests.get(
            TRANSCRIPT_API_URL,
            headers=headers,
            params=params,
            timeout=25,
        )
    except Exception as e:
        raise RuntimeError(f"TranscriptAPI request error: {e}")

    if resp.status_code != 200:
        raise RuntimeError(
            f"TranscriptAPI error {resp.status_code}: {resp.text}"
        )

    text = resp.text.strip()
    if not text:
        raise RuntimeError("TranscriptAPI returned empty transcript")

    return text