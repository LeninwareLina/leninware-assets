import os
import requests

TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")
BASE_URL = "https://api.transcriptapi.com/v1/transcript"

# Validate that the key actually exists
if not TRANSCRIPT_API_KEY:
    raise ValueError("TRANSCRIPT_API_KEY is missing. Add it in Railway variables.")

# NEW: Accept both old and new key formats
if not (TRANSCRIPT_API_KEY.startswith("tr_") or TRANSCRIPT_API_KEY.startswith("sk_")):
    print("⚠️ WARNING: TranscriptAPI key format unexpected. Continuing anyway.")


def get_youtube_transcript(video_id: str) -> str:
    """
    Retrieves transcript from TranscriptAPI.com using GET endpoint.
    """

    url = f"{BASE_URL}/{video_id}"

    headers = {
        "Authorization": f"Bearer {TRANSCRIPT_API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            return data.get("transcript", "")

        elif response.status_code == 404:
            raise RuntimeError("Transcript API error: Not Found")

        else:
            raise RuntimeError(
                f"Transcript API error: {response.status_code} - {response.text}"
            )

    except Exception as e:
        raise RuntimeError(f"Transcript API request failed: {e}")