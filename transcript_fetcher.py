# transcript_fetcher.py

import requests
from config import require_env, TRANSCRIPT_API_URL


def fetch_transcript(video_url: str) -> str:
    if not video_url:
        raise ValueError("fetch_transcript() called with empty video_url")

    api_key = require_env("TRANSCRIPT_API_KEY")

    # Must match TranscriptAPI spec
    base_url = TRANSCRIPT_API_URL.rstrip("/") + "/youtube/transcript"

    try:
        resp = requests.get(
            base_url,
            params={"video_url": video_url},   # <-- MUST be video_url
            headers={"Authorization": f"Bearer {api_key}"},
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