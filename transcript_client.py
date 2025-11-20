import os
import requests

import os
import requests

TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")

if not TRANSCRIPT_API_KEY:
    raise ValueError("TRANSCRIPT_API_KEY is missing. Add it in Railway variables.")

# Correct domain + correct path
BASE_URL = "https://transcriptapi.com/api/v1/transcript"


def get_video_id(url: str) -> str:
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    if "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    raise ValueError("Invalid YouTube URL. Cannot extract video ID.")


def get_video_transcript(url: str) -> str:
    video_id = get_video_id(url)
    request_url = f"{BASE_URL}/{video_id}"

    headers = {"Authorization": f"Bearer {TRANSCRIPT_API_KEY}"}

    try:
        response = requests.get(request_url, headers=headers, timeout=15)
    except Exception as e:
        raise RuntimeError(f"Transcript API request failed: {str(e)}")

    # Empty response body? Raise error
    if not response.text.strip():
        raise RuntimeError("Transcript API returned an empty response.")

    # Non-JSON body? Raise error
    try:
        data = response.json()
    except Exception:
        raise RuntimeError(f"Transcript API returned non-JSON data: {response.text[:200]}")

    if response.status_code == 404:
        raise RuntimeError("Transcript not found for this video.")

    if response.status_code != 200:
        raise RuntimeError(f"Transcript API error {response.status_code}: {response.text}")

    if "text" not in data or not data["text"].strip():
        raise RuntimeError("Transcript API returned no text.")

    return data["text"] = os.getenv("TRANSCRIPT_API_KEY")

if not TRANSCRIPT_API_KEY:
    raise ValueError("TRANSCRIPT_API_KEY is missing. Add it in Railway variables.")

# Using the root domain (not api.transcriptapi.com) due to DNS resolution issues on Railway
BASE_URL = "https://transcriptapi.com/v1/transcript"


def get_video_id(url: str) -> str:
    """
    Extracts YouTube video ID from any standard YouTube URL.
    """
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]

    if "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]

    raise ValueError("Invalid YouTube URL. Cannot extract video ID.")


def get_video_transcript(url: str) -> str:
    """
    Calls TranscriptAPI.com and returns the transcript text.
    """
    video_id = get_video_id(url)
    request_url = f"{BASE_URL}/{video_id}"

    headers = {"Authorization": f"Bearer {TRANSCRIPT_API_KEY}"}

    try:
        response = requests.get(request_url, headers=headers, timeout=15)
    except Exception as e:
        raise RuntimeError(f"Transcript API request failed: {str(e)}")

    if response.status_code == 404:
        raise RuntimeError("Transcript not found for this video.")

    if response.status_code != 200:
        raise RuntimeError(f"Transcript API error {response.status_code}: {response.text}")

    data = response.json()

    if "text" not in data or not data["text"].strip():
        raise RuntimeError("Transcript API returned no text.")

    return data["text"]