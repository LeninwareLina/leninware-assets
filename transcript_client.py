import os
import requests
import logging
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


def extract_video_id(youtube_url: str) -> str:
    """Extract YouTube video ID from any valid URL format."""
    parsed = urlparse(youtube_url)

    # youtu.be short link
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")

    # standard youtube.com link
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]

    raise RuntimeError(f"Could not extract video ID from URL: {youtube_url}")


def get_video_transcript(youtube_url: str) -> str:
    """Fetch transcript using TranscriptAPI.com."""
    token = os.getenv("TRANSCRIPT_API_TOKEN")
    if not token:
        raise RuntimeError("TRANSCRIPT_API_TOKEN is missing from environment variables")

    video_id = extract_video_id(youtube_url)
    url = f"https://transcriptapi.com/api/v1/{video_id}?token={token}"

    logger.info(f"Requesting transcript from TranscriptAPI.com")

    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError(f"Transcript API error: {r.text}")

    data = r.json()

    if "transcript" not in data or not data["transcript"]:
        raise RuntimeError("Transcript unavailable. No Leninware outputs can be produced.")

    return data["transcript"]