import os
from typing import Optional

import requests

TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")


class TranscriptError(Exception):
    """Raised when fetching a transcript fails."""


BASE_URL = "https://transcriptapi.com/api/v2/youtube/transcript"


def _ensure_api_key() -> str:
    if not TRANSCRIPT_API_KEY:
        raise TranscriptError("TRANSCRIPT_API_KEY environment variable is not set.")
    return TRANSCRIPT_API_KEY


def fetch_transcript_via_transcriptapi(video_url: str) -> str:
    """
    Fetch transcript via TranscriptAPI.com (v2).

    - Uses format='text' so we get Markdown with metadata in a 'content' field.
    - Returns the Markdown string.
    """
    api_key = _ensure_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    params = {
        "video_url": video_url,
        "format": "text",
    }

    try:
        resp = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
    except requests.RequestException as e:
        raise TranscriptError(f"TranscriptAPI request failed: {e}") from e

    if resp.status_code == 404:
        # Known / nice error for Telegram logs
        raise TranscriptError("TranscriptAPI: transcript not found (404)")

    if resp.status_code == 401:
        raise TranscriptError("TranscriptAPI: unauthorized (401) – check API key.")

    if resp.status_code >= 400:
        # Try to show something meaningful
        try:
            err_json = resp.json()
        except Exception:
            err_json = resp.text
        raise TranscriptError(
            f"TranscriptAPI error {resp.status_code}: {err_json}"
        )

    try:
        data = resp.json()
    except ValueError as e:
        raise TranscriptError(f"TranscriptAPI: invalid JSON response: {e}") from e
# DEBUG LOG — TEMPORARY
import logging
logger = logging.getLogger(__name__)
logger.error("TranscriptAPI raw response: %s", data)

content = data.get("content")
if not content or not isinstance(content, str):
    raise TranscriptError("TranscriptAPI: response missing 'content' field.")