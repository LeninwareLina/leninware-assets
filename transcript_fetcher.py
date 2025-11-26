# transcript_fetcher.py

import requests

from config import (
    TRANSCRIPT_API_KEY,
    TRANSCRIPT_API_URL,
    require_env,
)


def fetch_transcript(video_url: str) -> str:
    """
    Fetch a transcript from TranscriptAPI for the given YouTube URL.

    Returns a raw transcript string.
    Raises RuntimeError on failure.
    """
    if not video_url:
        raise ValueError("fetch_transcript() called with empty video_url")

    api_key = require_env("TRANSCRIPT_API_KEY", TRANSCRIPT_API_KEY)
    base_url = require_env("TRANSCRIPT_API_URL", TRANSCRIPT_API_URL)

    params = {"url": video_url}
    headers = {"x-api-key": api_key}

    try:
        resp = requests.get(
            base_url,
            params=params,
            headers=headers,
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