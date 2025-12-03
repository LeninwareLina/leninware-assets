# transcript_fetcher.py

import re
import requests
from config import TRANSCRIPT_API_KEY


TRANSCRIPT_API_URL = "https://transcriptapi.com/api/v2/youtube/transcript"


def _extract_video_id(url_or_id: str) -> str:
    """
    Extracts YouTube video ID from URLs or returns a raw ID.
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

    # Assume raw ID
    return url_or_id.strip()


def fetch_transcript(video_url_or_id: str) -> str | None:
    """
    Fetches the transcript text from transcriptAPI.com.
    Returns None if unavailable or if API returns an error.
    """

    video_id = _extract_video_id(video_url_or_id)

    headers = {
        "Authorization": f"Bearer {TRANSCRIPT_API_KEY}"
    }

    params = {
        "video_url": video_id,     # they accept raw ID
        "format": "json"
    }

    try:
        resp = requests.get(
            TRANSCRIPT_API_URL,
            params=params,
            headers=headers,
            timeout=30
        )

        if resp.status_code != 200:
            print(f"[transcript] HTTP error {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()

        # Official docs: transcript = data['transcript']
        transcript = data.get("transcript")
        if not transcript:
            print("[transcript] Transcript not available.")
            return None

        # transcript is a list of chunks: [{text, start, duration}, ...]
        if isinstance(transcript, list):
            return " ".join([chunk.get("text", "") for chunk in transcript])

        # Or a raw string (rare)
        if isinstance(transcript, str):
            return transcript

        print("[transcript] Unexpected response format.")
        return None

    except Exception as e:
        print("[transcript] Exception while fetching transcript:", e)
        return None