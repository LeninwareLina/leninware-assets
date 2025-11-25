# ---------------------------------------------------------------------------
# transcript_fetcher.py (rewritten)
# ---------------------------------------------------------------------------

import requests

TRANSCRIPT_ENDPOINT = "https://api.transcriptapi.com/v1/fetch"  # example placeholder


def fetch_transcript(video_id: str) -> str:
    """
    Fetch transcript cleanly.
    Raises clean errors and prevents bad data from contaminating model context.
    """

    if not video_id:
        raise ValueError("No YouTube video_id provided.")

    try:
        r = requests.get(TRANSCRIPT_ENDPOINT, params={"id": video_id}, timeout=20)
        r.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"TranscriptAPI request failed: {e}")

    data = r.json()

    # Defensive validation
    if not data or "transcript" not in data:
        raise RuntimeError("TranscriptAPI returned invalid response structure.")

    text = data.get("transcript", "").strip()

    if not text:
        raise RuntimeError("TranscriptAPI returned empty transcript.")

    return text