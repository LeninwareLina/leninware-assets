import re
from typing import Optional

import requests

from config import require_env, TRANSCRIPT_API_V2_URL

# Handles normal watch URLs, youtu.be and shorts links
YOUTUBE_ID_RE = re.compile(
    r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})"
)


def _extract_video_id(url: str) -> Optional[str]:
    """Pull a YouTube video ID out of a URL or raw ID."""
    # If it's already an 11-char ID, accept it
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url

    m = YOUTUBE_ID_RE.search(url)
    if m:
        return m.group(1)

    return None


def fetch_transcript(video_url: str) -> Optional[str]:
    """Fetch a transcript for a YouTube video using TranscriptAPI.

    Returns transcript text, or None if not available.
    """
    api_key = require_env("TRANSCRIPT_API_KEY")

    video_id = _extract_video_id(video_url)
    if not video_id:
        print(f"[transcript] Could not extract video id from URL: {video_url}")
        return None

    try:
        resp = requests.get(
            TRANSCRIPT_API_V2_URL,
            headers={"x-api-key": api_key},
            params={"platform": "youtube", "video_id": video_id},
            timeout=30,
        )
    except Exception as e:
        print(f"[transcript] TranscriptAPI request error: {e}")
        return None

    if resp.status_code == 404:
        print("[transcript] Transcript not found for this video")
        return None

    if resp.status_code != 200:
        print(f"[transcript] TranscriptAPI error {resp.status_code}: {resp.text[:200]}")
        return None

    try:
        data = resp.json()
    except ValueError:
        print("[transcript] Non-JSON response from TranscriptAPI")
        return None

    # Flexibly handle different shapes: segments, lines, or raw transcript
    transcript_text = ""

    if isinstance(data, dict):
        if isinstance(data.get("segments"), list):
            parts = [seg.get("text", "") for seg in data["segments"]]
            transcript_text = "\n".join(p for p in parts if p)
        elif isinstance(data.get("lines"), list):
            parts = [ln.get("text", "") for ln in data["lines"]]
            transcript_text = "\n".join(p for p in parts if p)
        elif isinstance(data.get("transcript"), str):
            transcript_text = data["transcript"]
        else:
            transcript_text = str(data)
    else:
        transcript_text = str(data)

    transcript_text = transcript_text.strip()
    if not transcript_text:
        print("[transcript] Empty transcript returned from TranscriptAPI")
        return None

    return transcript_text