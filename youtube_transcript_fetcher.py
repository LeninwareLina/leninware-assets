import os
import requests
from urllib.parse import urlparse, parse_qs


class TranscriptError(Exception):
    """Custom error for transcript retrieval problems."""
    pass


# TranscriptAPI.com endpoint
TRANSCRIPT_API_BASE = "https://transcriptapi.com/api/v1/transcript"
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")


def extract_video_id(url_or_id: str) -> str:
    """
    Takes a YouTube URL or a raw video ID and returns the 11-character ID.
    This properly strips Telegram's ?si=… junk and extra parameters.
    """
    url_or_id = (url_or_id or "").strip()

    # Looks like URL?
    if url_or_id.startswith("http://") or url_or_id.startswith("https://"):
        parsed = urlparse(url_or_id)
        hostname = (parsed.hostname or "").lower()

        # Standard YouTube link: youtube.com/watch?v=ID
        if "youtube.com" in hostname:
            query = parse_qs(parsed.query)
            if "v" in query and query["v"]:
                return query["v"][0]

        # Short link: youtu.be/ID
        if "youtu.be" in hostname:
            vid = parsed.path.lstrip("/")
            if vid:
                return vid

    # If not a URL, assume it's already a video ID
    return url_or_id


def fetch_youtube_transcript(url_or_id: str):
    """
    Fetches transcript + title + channel from TranscriptAPI.com.

    Returns:
        transcript_text (str),
        video_title (str),
        channel_name (str)

    Raises:
        TranscriptError for any failure.
    """
    if not TRANSCRIPT_API_KEY:
        raise TranscriptError("TRANSCRIPT_API_KEY environment variable is not set")

    video_id = extract_video_id(url_or_id)
    if not video_id:
        raise TranscriptError("Could not extract a YouTube video ID from input")

    headers = {
        "Authorization": f"Bearer {TRANSCRIPT_API_KEY}"
    }

    params = {
        "video_url": video_id,
        "format": "text",
        "include_metadata": "true"
    }

    try:
        response = requests.get(
            TRANSCRIPT_API_BASE,
            headers=headers,
            params=params,
            timeout=30
        )
    except requests.RequestException as e:
        raise TranscriptError(f"TranscriptAPI request failed: {e}")

    # HTTP error handling
    if response.status_code == 404:
        raise TranscriptError("TranscriptAPI: transcript not found (404)")
    if response.status_code == 401:
        raise TranscriptError("TranscriptAPI: unauthorized (check API key)")
    if not response.ok:
        snippet = response.text[:200].replace("\n", " ")
        raise TranscriptError(
            f"TranscriptAPI HTTP {response.status_code}: {snippet}"
        )

    # Parse JSON
    try:
        data = response.json()
    except ValueError:
        raise TranscriptError("TranscriptAPI returned invalid JSON")

    transcript_text = data.get("transcript") or ""
    metadata = data.get("metadata") or {}

    video_title = (
        metadata.get("title")
        or metadata.get("video_title")
        or ""
    )

    channel_name = (
        metadata.get("channel_name")
        or metadata.get("channelTitle")
        or metadata.get("author")
        or ""
    )

    if not transcript_text:
        raise TranscriptError("TranscriptAPI returned an empty transcript")

    return transcript_text, video_title, channel_name