# youtube_transcript_fetcher.py
import os
import requests

TRANSCRIPT_API_URL = "https://transcriptapi.com/api/v2/youtube/transcript"
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")

def fetch_transcript(video_url: str) -> str:
    if not TRANSCRIPT_API_KEY:
        raise RuntimeError("TRANSCRIPT_API_KEY missing")

    params = {
        "video_url": video_url,
        "format": "text",
        "send_metadata": "true",
        "include_timestamp": "true"
    }

    headers = {
        "Authorization": f"Bearer {TRANSCRIPT_API_KEY}"
    }

    response = requests.get(TRANSCRIPT_API_URL, params=params, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(f"TranscriptAPI error {response.status_code}: {response.text}")

    data = response.json()

    if "content" not in data:
        raise RuntimeError("TranscriptAPI: response missing 'content' field")

    return data["content"]