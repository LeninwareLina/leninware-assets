import os
import requests
from typing import Optional


TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")
TRANSCRIPT_API_URL = "https://transcriptapi.com/api/v1/transcript"


class TranscriptError(Exception):
    """Raised when we cannot get a transcript for a video."""


def fetch_transcript_via_service(video_url: str) -> str:
    """
    Fetch the transcript as plain text from TranscriptAPI.com.

    `video_url` can be either a full YouTube URL or a bare video ID.
    We just pass it through in the `video_url` parameter.
    """
    if not TRANSCRIPT_API_KEY:
        raise TranscriptError("Missing TRANSCRIPT_API_KEY environment variable")

    if not video_url:
        raise TranscriptError("Empty video URL")

    headers = {
        "Authorization": f"Bearer {TRANSCRIPT_API_KEY}",
    }
    params = {
        "video_url": video_url,
        "format": "text",  # plain text body
    }

    try:
        resp = requests.get(
            TRANSCRIPT_API_URL,
            headers=headers,
            params=params,
            timeout=30,
        )
    except requests.RequestException as e:
        raise TranscriptError(f"Network error talking to TranscriptAPI: {e}") from e

    if resp.status_code == 404:
        # Service explicitly says no transcript for this video.
        raise TranscriptError("TranscriptAPI: transcript not found (404)")

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise TranscriptError(
            f"TranscriptAPI HTTP {resp.status_code}: {resp.text[:200]}"
        ) from e

    text = resp.text.strip()
    if not text:
        raise TranscriptError("TranscriptAPI returned empty transcript")

    return text