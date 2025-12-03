# transcript_fetcher.py

import re
import requests
from config import USE_MOCK_AI, TRANSCRIPT_API_KEY

TRANSCRIPT_API_URL = "https://transcriptapi.com/api/v2/youtube/transcript"


def _extract_video_id(url_or_id: str) -> str:
    """
    Extracts a YouTube ID from many common URL formats.
    If no pattern matches, returns the raw value.
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
    return url_or_id.strip()


def fetch_transcript(video_url_or_id: str) -> str | None:
    """
    Fetch transcript from transcriptAPI.com.
    In MOCK MODE, returns a fixed dummy transcript instead of calling API.
    """

    video_id = _extract_video_id(video_url_or_id)

    # ----------------------------------------------------
    # MOCK MODE — return free dummy transcript
    # ----------------------------------------------------
    if USE_MOCK_AI:
        return (
            "This is a mock transcript for video ID "
            f"{video_id}. It simulates a real transcript so "
            "the pipeline can run without using TranscriptAPI."
        )

    # ----------------------------------------------------
    # REAL MODE — call transcriptAPI.com
    # ----------------------------------------------------
    headers = {
        "Authorization": f"Bearer {TRANSCRIPT_API_KEY}"
    }

    params = {
        "video_url": video_id,
        "format": "json",
    }

    try:
        resp = requests.get(
            TRANSCRIPT_API_URL,
            params=params,
            headers=headers,
            timeout=30,
        )

        if resp.status_code != 200:
            print(f"[transcript] HTTP error {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()

        transcript = data.get("transcript")
        if not transcript:
            print("[transcript] Transcript not available.")
            return None

        # transcriptAPI normally returns a list of chunks
        if isinstance(transcript, list):
            return " ".join(chunk.get("text", "") for chunk in transcript)

        # Rare: raw string
        if isinstance(transcript, str):
            return transcript

        print("[transcript] Unexpected transcript format.")
        return None

    except Exception as e:
        print("[transcript] Exception while fetching transcript:", e)
        return None