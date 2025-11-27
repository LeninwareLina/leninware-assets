import re
from typing import Optional

import requests

from config import TRANSCRIPT_API_KEY

# Official v2 endpoint from TranscriptAPI docs
API_URL = "https://api.transcriptapi.com/api/v2/video-transcript"

# Handles normal watch URLs, youtu.be and shorts links
YOUTUBE_ID_RE = re.compile(
    r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})"
)


def extract_video_id(url: str) -> Optional[str]:
    """Pull a YouTube video ID out of a URL."""
    match = YOUTUBE_ID_RE.search(url)
    return match.group(1) if match else None


def fetch_transcript(video_url: str) -> Optional[str]:
    """
    Fetch a transcript from TranscriptAPI for a given YouTube URL.

    Returns the transcript text, or None if not available / error.
    """
    if not TRANSCRIPT_API_KEY:
        print("Set TRANSCRIPT_API_KEY in your environment first")
        return None

    video_id = extract_video_id(video_url)
    if not video_id:
        print(f"[worker] Could not extract video id from URL: {video_url}")
        return None

    try:
        resp = requests.get(
            API_URL,
            headers={"x-api-key": TRANSCRIPT_API_KEY},
            params={"platform": "youtube", "video_id": video_id},
            timeout=30,
        )
    except Exception as e:
        print(f"[worker] TranscriptAPI request error: {e}")
        return None

    if resp.status_code == 404:
        print("[worker] Transcript not found for this video")
        return None

    if resp.status_code != 200:
        print(f"[worker] TranscriptAPI error {resp.status_code}: {resp.text[:200]}")
        return None

    data = resp.json()

    # Be flexible about the response shape; handle both v1/v2 style payloads.
    transcript_text = ""

    if isinstance(data, dict):
        if "segments" in data:
            parts = [seg.get("text", "") for seg in data["segments"]]
            transcript_text = "\n".join(p for p in parts if p)
        elif "lines" in data:
            parts = [ln.get("text", "") for ln in data["lines"]]
            transcript_text = "\n".join(p for p in parts if p)
        elif isinstance(data.get("transcript"), str):
            transcript_text = data["transcript"]
        else:
            # Fallback: best-effort stringification
            transcript_text = str(data)
    else:
        transcript_text = str(data)

    transcript_text = transcript_text.strip()
    if not transcript_text:
        print("[worker] Empty transcript returned from TranscriptAPI")
        return None

    return transcript_text