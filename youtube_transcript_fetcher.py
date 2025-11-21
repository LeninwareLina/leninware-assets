import os
import re
import requests


BASE_URL = "https://transcriptapi.com/api/v1/transcript/"
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")


class TranscriptError(Exception):
    pass


def extract_video_id(url_or_id: str) -> str:
    """
    Accepts either a raw YouTube video ID or a full URL and
    returns the video ID.
    """
    # If it looks like a URL, pull the ID out
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        # Handles:
        #  - https://www.youtube.com/watch?v=ID
        #  - https://youtu.be/ID
        #  - https://youtu.be/ID?si=...
        match = re.search(r"(v=|youtu\.be/)([\w-]+)", url_or_id)
        if match:
            return match.group(2)

    # Otherwise assume it's already an ID
    return url_or_id.strip()


def fetch_youtube_transcript(url_or_id: str) -> str:
    """
    Fetch transcript via transcriptAPI.com.

    Requires:
        TRANSCRIPT_API_KEY  (env var)
    """
    if not TRANSCRIPT_API_KEY:
        raise TranscriptError("Missing TRANSCRIPT_API_KEY environment variable")

    video_id = extract_video_id(url_or_id)
    url = BASE_URL + video_id

    headers = {
        "X-Api-Key": TRANSCRIPT_API_KEY
    }

    try:
        resp = requests.get(url, headers=headers, timeout=30)
    except Exception as e:
        raise TranscriptError(f"Request to transcriptAPI failed: {e}")

    if resp.status_code == 404:
        raise TranscriptError("TranscriptAPI: transcript not found (404)")

    if resp.status_code == 401 or resp.status_code == 403:
        raise TranscriptError(
            f"TranscriptAPI auth error ({resp.status_code}). "
            "Check TRANSCRIPT_API_KEY."
        )

    if resp.status_code >= 500:
        raise TranscriptError(
            f"TranscriptAPI server error ({resp.status_code}). Try again later."
        )

    # Some implementations sometimes return plain text like "Not Found"
    # so we defensively handle non-JSON too.
    try:
        data = resp.json()
    except ValueError:
        txt = resp.text.strip()
        if not txt:
            raise TranscriptError("TranscriptAPI returned empty response")
        # If it's just plain text, treat it as the transcript.
        return txt

    # Try to extract transcript in a few common shapes
    transcript = None

    if isinstance(data, dict):
        if isinstance(data.get("transcript"), str):
            transcript = data["transcript"]
        elif isinstance(data.get("transcript"), list):
            # e.g. [{"text": "...", "start": ..., "duration": ...}, ...]
            parts = []
            for entry in data["transcript"]:
                if isinstance(entry, dict) and "text" in entry:
                    parts.append(str(entry["text"]))
            transcript = " ".join(parts).strip()
        elif "text" in data and isinstance(data["text"], str):
            transcript = data["text"]

    elif isinstance(data, list):
        # list of segments with "text"
        parts = []
        for entry in data:
            if isinstance(entry, dict) and "text" in entry:
                parts.append(str(entry["text"]))
        transcript = " ".join(parts).strip()

    if not transcript:
        raise TranscriptError(
            f"TranscriptAPI JSON did not contain a usable transcript: {data}"
        )

    return transcript