# transcript_fetcher.py

import re
import requests
from config import TRANSCRIPT_API_KEY


TRANSCRIPT_API_URL = "https://transcriptapi.com/v1/youtube"


def _extract_video_id(url_or_id: str) -> str:
    """
    Extracts YouTube video ID from various URL formats.
    Assumes ingest has already filtered Shorts and non-standard formats.
    """
    patterns = [
        r"v=([A-Za-z0-9_-]{6,})",
        r"youtu\.be/([A-Za-z0-9_-]{6,})",
        r"watch/([A-Za-z0-9_-]{6,})",
    ]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)

    # If no match, assume raw ID
    return url_or_id.strip()


def fetch_transcript(video_url_or_id: str) -> str | None:
    """
    Attempts to fetch transcript via TranscriptAPI /v1/youtube.
    Returns None if unavailable (safe for pipeline).
    """
    video_id = _extract_video_id(video_url_or_id)

    headers = {
        "Authorization": f"Bearer {TRANSCRIPT_API_KEY}"
    }

    params = {
        # v1 endpoint uses video_url, not video_id
        "video_url": f"https://www.youtube.com/watch?v={video_id}"
    }

    resp = requests.get(TRANSCRIPT_API_URL, params=params, headers=headers)

    if resp.status_code != 200:
        print(f"[transcript] API error {resp.status_code}: {resp.text[:150]}")
        return None

    data = resp.json()

    transcript_text = data.get("transcript")
    if not transcript_text:
        print("[transcript] Transcript not available.")
        return None

    return transcript_text