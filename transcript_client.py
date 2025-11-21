import os
import requests


BASE_URL = "https://api.transcriptapi.com/api/v1/transcript"


def get_video_id(url: str) -> str:
    """
    Extract the YouTube video ID from a URL.
    Works with youtu.be and youtube.com links.
    """
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]

    if "youtube.com/watch" in url and "v=" in url:
        return url.split("v=")[1].split("&")[0]

    raise ValueError("Could not extract video ID from URL.")


def get_video_transcript(url: str) -> str:
    """
    Fetch transcript text from TranscriptAPI.com.
    Returns transcript string.
    Raises ValueError if no transcript OR if API error occurs.
    """

    api_key = os.getenv("TRANSCRIPT_API_KEY")

    if not api_key:
        raise ValueError("TRANSCRIPT_API_KEY is missing. Add it in Railway variables.")

    video_id = get_video_id(url)

    endpoint = f"{BASE_URL}/{video_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(endpoint, headers=headers, timeout=20)

    except Exception as e:
        raise ValueError(f"Transcript API request failed: {e}")

    # Non-JSON means API returned an error page (e.g. Not Found)
    try:
        data = response.json()
    except Exception:
        raise ValueError(f"Transcript API returned non-JSON data: {response.text}")

    if response.status_code == 404:
        raise ValueError("Transcript unavailable for this video.")

    if response.status_code != 200:
        raise ValueError(f"Transcript API error: {response.text}")

    if "text" not in data:
        raise ValueError("Transcript API returned invalid structure (missing 'text').")

    return data["text"]