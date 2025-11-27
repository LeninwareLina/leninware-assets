import os
import requests
import time

TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")

if not TRANSCRIPT_API_KEY:
    raise RuntimeError("TRANSCRIPT_API_KEY not set in environment")

TRANSCRIPT_ENDPOINT = "https://transcriptapi.com/api/v1/transcript"


def fetch_transcript(video_url, retries=5, backoff=2):
    """
    Fetch transcript for a YouTube video using TranscriptAPI.
    Retries automatically on connection failures.
    """
    for attempt in range(retries):
        try:
            response = requests.post(
                TRANSCRIPT_ENDPOINT,
                json={"url": video_url},
                headers={"x-api-key": TRANSCRIPT_API_KEY},
                timeout=30,
            )

            # Good response
            if response.status_code == 200:
                data = response.json()
                return data.get("transcript", "")

            # Not found or no transcript available
            if response.status_code in (400, 404):
                return ""

            # Otherwise: treat as temporary server error
            print(
                f"[TranscriptAPI] HTTP {response.status_code}: {response.text}. "
                f"Retrying ({attempt+1}/{retries})..."
            )

        except requests.exceptions.RequestException as e:
            print(
                f"[TranscriptAPI] Network error: {e}. "
                f"Retrying ({attempt+1}/{retries})..."
            )

        time.sleep(backoff)

    print("[TranscriptAPI] FAILED after retries.")
    return ""