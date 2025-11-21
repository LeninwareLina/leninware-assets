import os
import requests
import re

API_KEY = os.getenv("TRANSCRIPT_API_KEY")

def extract_video_id(url_or_id: str) -> str:
    """
    Takes either a YouTube URL or a raw ID
    and returns the video ID.
    """
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        match = re.search(r"(v=|youtu\.be/)([\w-]+)", url_or_id)
        if match:
            return match.group(2)
    return url_or_id


def fetch_youtube_transcript(url_or_id: str):
    """
    Fetches transcript + metadata via TranscriptAPI.com
    Returns (transcript_text, title, channel)
    Raises exceptions with clean explanations.
    """

    if not API_KEY:
        raise RuntimeError("TRANSCRIPT_API_KEY not set in environment variables.")

    video_id = extract_video_id(url_or_id)

    url = "https://transcriptapi.com/api/v1/transcript"
    params = {"video_url": video_id}
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise RuntimeError("TranscriptAPI: transcript not found (404)")
        elif response.status_code == 401:
            raise RuntimeError("TranscriptAPI: unauthorized (401). Wrong API key?")
        else:
            raise RuntimeError(f"TranscriptAPI HTTP error: {e}")

    data = response.json()

    transcript_items = data.get("transcript", [])
    transcript_text = " ".join([entry["text"] for entry in transcript_items])

    metadata = data.get("metadata", {})
    title = metadata.get("title", "Unknown Title")
    channel = metadata.get("channel_name", "Unknown Channel")

    return transcript_text, title, channel