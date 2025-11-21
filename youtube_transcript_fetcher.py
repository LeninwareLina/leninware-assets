# youtube_transcript_fetcher.py

import os
from typing import Optional
from urllib.parse import urlparse, parse_qs

import requests


TRANSCRIPT_API_BASE_URL = "https://transcriptapi.com/api/v2"


class TranscriptError(Exception):
    """Raised when we can't get a transcript from any source."""
    pass


def _get_env_api_key() -> str:
    api_key = os.getenv("TRANSCRIPT_API_KEY")
    if not api_key:
        raise TranscriptError(
            "TRANSCRIPT_API_KEY environment variable is not set. "
            "Please add it in Railway."
        )
    return api_key


def _normalise_youtube_url(url: str) -> str:
    """
    TranscriptAPI accepts either:
      - full YouTube URL (what your personal Claude sends), or
      - just the 11-char video ID.

    To stay as close as possible to your working setup, we pass
    the original URL through untouched, but we still sanity-check it.
    """
    url = url.strip()

    # If it's already an 11-character ID, just return it.
    if len(url) == 11 and " " not in url and "/" not in url:
        return url

    parsed = urlparse(url)

    # Short links like https://youtu.be/VIDEO_ID
    if parsed.netloc in {"youtu.be"} and parsed.path:
        vid = parsed.path.lstrip("/")
        if len(vid) == 11:
            return url  # full URL is fine

    # Standard links like https://www.youtube.com/watch?v=VIDEO_ID
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        vid_list = qs.get("v")
        if vid_list and len(vid_list[0]) == 11:
            return url  # again, full URL is fine

    # If it's something weird, still let TranscriptAPI decide.
    return url


def fetch_transcript_via_service(video_url: str) -> str:
    """
    Fetch a YouTube transcript using TranscriptAPI.com (v2).

    We mirror what your personal Claude does:

      GET https://transcriptapi.com/api/v2/youtube/transcript
          ?video_url=<url or id>
          &format=text
          &send_metadata=true
          &include_timestamp=true

    Response (for format=text) looks like:
      { "content": "<markdown transcript here>" }
    """
    api_key = _get_env_api_key()
    cleaned_url = _normalise_youtube_url(video_url)

    params = {
        "video_url": cleaned_url,
        "format": "text",           # <- as you confirmed
        "send_metadata": "true",
        "include_timestamp": "true",
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        resp = requests.get(
            f"{TRANSCRIPT_API_BASE_URL}/youtube/transcript",
            params=params,
            headers=headers,
            timeout=60,
        )
    except requests.RequestException as e:
        raise TranscriptError(f"Network error talking to TranscriptAPI: {e}") from e

    # Helpful, explicit error messages
    if resp.status_code == 401:
        raise TranscriptError(
            "TranscriptAPI returned 401 Unauthorized. "
            "Double-check your TRANSCRIPT_API_KEY in Railway."
        )

    if resp.status_code == 404:
        # This *now* really means "no transcript", not "wrong endpoint"
        raise TranscriptError("TranscriptAPI: transcript not found (404).")

    if not resp.ok:
        # Any other status code – surface some detail for debugging
        text = resp.text[:500]
        raise TranscriptError(
            f"TranscriptAPI error {resp.status_code}: {text}"
        )

    try:
        data = resp.json()
    except ValueError as e:
        raise TranscriptError(
            f"TranscriptAPI returned non-JSON response: {resp.text[:200]}"
        ) from e

    content: Optional[str] = data.get("content")
    if not content:
        raise TranscriptError(
            "TranscriptAPI response did not contain a 'content' field. "
            f"Raw JSON: {data}"
        )

    return content