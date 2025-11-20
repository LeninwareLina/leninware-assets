import os
import requests
import logging
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

# Get TranscriptAPI key from Railway
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")
if not TRANSCRIPT_API_KEY:
    raise ValueError("TRANSCRIPT_API_KEY is missing. Add it in Railway variables.")

# Base URL for TranscriptAPI – adjust if their docs say otherwise
BASE_URL = "https://api.transcriptapi.com/v1/transcript"


def _extract_video_id(youtube_url: str) -> str:
    """Extract YouTube video ID from common URL formats."""
    parsed = urlparse(youtube_url)

    # Short youtu.be links
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")

    # Standard youtube.com links
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]

    raise ValueError(f"Could not extract video ID from URL: {youtube_url}")


def get_video_transcript(youtube_url: str) -> str:
    """
    Fetch the transcript text for a YouTube video using TranscriptAPI.com.
    Returns plain text. Raises RuntimeError if unavailable.
    """
    video_id = _extract_video_id(youtube_url)
    url = f"{BASE_URL}/{video_id}"

    headers = {
        "Authorization": f"Bearer {TRANSCRIPT_API_KEY}"
    }

    logger.info(f"Requesting transcript for video_id={video_id} from TranscriptAPI")

    try:
        resp = requests.get(url, headers=headers, timeout=20)

        if resp.status_code == 200:
            data = resp.json()
            text = data.get("transcript") or ""
            if not text.strip():
                raise RuntimeError("TranscriptAPI returned an empty transcript.")
            logger.info(f"Transcript length: {len(text)} characters")
            return text

        if resp.status_code == 404:
            raise RuntimeError("Transcript unavailable. No Leninware outputs can be produced.")

        # Any other status is treated as a hard error
        raise RuntimeError(f"Transcript API error {resp.status_code}: {resp.text}")

    except Exception as e:
        logger.error(f"Transcript API request failed: {e}")
        raise RuntimeError(f"Transcript API request failed: {e}")