import re
import requests
from config import USE_MOCK_AI, TRANSCRIPT_API_KEY

TRANSCRIPT_API_URL = "https://transcriptapi.com/api/v2/youtube/transcript"


def _extract_video_id(url_or_id: str) -> str:
    """
    Extracts a YouTube ID from many common URL formats.
    If no pattern matches, returns the raw value.
    """
    patterns = [
        r"v=([A-Za-z0-9_-]{6,})",
        r"youtu\.be/([A-Za-z0-9_-]{6,})",
        r"watch/([A-Za-z0-9_-]{6,})",
    ]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            extracted = m.group(1)
            print(f"[transcript] Extracted video ID: {extracted}")
            return extracted

    print(f"[transcript] Using raw ID: {url_or_id.strip()}")
    return url_or_id.strip()


def fetch_transcript(video_url_or_id: str) -> str | None:
    """
    Fetch transcript from transcriptAPI.com.
    In MOCK MODE, returns a fixed dummy transcript instead of calling API.
    """

    print(f"[transcript] Fetching transcript for: {video_url_or_id}")

    video_id = _extract_video_id(video_url_or_id)

    # ----------------------------------------------------
    # MOCK MODE — return free dummy transcript
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print(f"[transcript:mock] Returning mock transcript for {video_id}")
        return (
            "This is a mock transcript for video ID "
            f"{video_id}. It simulates a real transcript so "
            "the pipeline can run without using TranscriptAPI."
        )

    # ----------------------------------------------------
    # REAL MODE — call transcriptAPI.com
    # ----------------------------------------------------
    headers = {
        "Authorization": f"Bearer {TRANSCRIPT_API_KEY}"
    }

    params = {
        "video_url": video_id,
        "format": "json",
    }

    print(f"[transcript] Requesting transcript from API: {TRANSCRIPT_API_URL}")
    print(f"[transcript] Params: {params}")

    try:
        resp = requests.get(
            TRANSCRIPT_API_URL,
            params=params,
            headers=headers,
            timeout=30,
        )
    except Exception as e:
        print(f"[transcript] NETWORK ERROR fetching transcript: {e}")
        return None

    # Not 200 → fail
    if resp.status_code != 200:
        print(f"[transcript] HTTP {resp.status_code} — {resp.text[:300]}")
        return None

    # Try JSON parse
    try:
        data = resp.json()
    except Exception as e:
        print(f"[transcript] ERROR parsing JSON: {e}")
        return None

    # API-level errors
    if "error" in data:
        print(f"[transcript] API ERROR: {data['error']}")
        return None

    transcript = data.get("transcript")
    if not transcript:
        print("[transcript] Transcript missing or empty in API response")
        return None

    # transcriptAPI usually returns list of chunks
    if isinstance(transcript, list):
        print(f"[transcript] Received {len(transcript)} transcript chunks")
        merged = " ".join(chunk.get("text", "") for chunk in transcript)
        print(f"[transcript] Transcript merged length: {len(merged)} chars")
        return merged

    # Rare: raw string
    if isinstance(transcript, str):
        print(f"[transcript] Received raw transcript string ({len(transcript)} chars)")
        return transcript

    print(f"[transcript] Unexpected transcript format: {type(transcript)}")
    return None