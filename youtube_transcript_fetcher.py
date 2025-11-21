import os
import re
import requests


class TranscriptError(Exception):
    """Raised when fetching a transcript fails."""
    pass


def _extract_video_id(url_or_id: str) -> str:
    """
    Accept either a full YouTube URL or a raw video ID and return the ID.
    """
    url_or_id = url_or_id.strip()

    # If it's already 11-char ID, just use it
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
        return url_or_id

    # Common YouTube URL patterns
    patterns = [
        r"v=([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
    ]

    for pat in patterns:
        m = re.search(pat, url_or_id)
        if m:
            return m.group(1)

    raise TranscriptError(f"Could not extract video ID from: {url_or_id}")


def fetch_transcript_via_service(url_or_id: str):
    """
    Fetch transcript + metadata from TranscriptAPI.com.

    Returns:
        (transcript_text, video_title, channel_name, canonical_video_url)
    """
    api_key = os.getenv("TRANSCRIPT_API_KEY")
    if not api_key:
        raise TranscriptError("Missing TRANSCRIPT_API_KEY environment variable")

    video_id = _extract_video_id(url_or_id)

    base_url = "https://transcriptapi.com/api/v1/transcript"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    # Per docs: they accept video_url=VIDEO_ID (11-char ID)
    params = {
        "video_url": video_id,
        # no explicit format so we get full JSON (segments + metadata)
    }

    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=30)
    except requests.RequestException as e:
        raise TranscriptError(f"Request to TranscriptAPI failed: {e}")

    if resp.status_code == 404:
        # Align with Claude prompt expectations
        raise TranscriptError("Transcript unavailable. No Leninware outputs can be produced.")

    if not resp.ok:
        raise TranscriptError(
            f"TranscriptAPI error {resp.status_code}: {resp.text[:300]}"
        )

    try:
        data = resp.json()
    except ValueError as e:
        raise TranscriptError(f"Failed to parse TranscriptAPI response as JSON: {e}")

    transcript_field = data.get("transcript")
    if not transcript_field:
        raise TranscriptError("TranscriptAPI response missing 'transcript' field")

    # They sometimes return list of segments, sometimes plain string.
    if isinstance(transcript_field, list):
        transcript_text = " ".join(seg.get("text", "") for seg in transcript_field)
    elif isinstance(transcript_field, str):
        transcript_text = transcript_field
    else:
        raise TranscriptError("Unexpected 'transcript' format in response")

    transcript_text = transcript_text.strip()
    if not transcript_text:
        raise TranscriptError("Transcript text is empty")

    metadata = data.get("metadata", {}) or {}
    video_title = metadata.get("title", "").strip() or ""
    # Channel might be stored under different names; try a few
    channel_name = (
        metadata.get("channel")
        or metadata.get("author")
        or metadata.get("uploader")
        or ""
    )
    channel_name = str(channel_name).strip()

    canonical_url = f"https://www.youtube.com/watch?v={video_id}"

    return transcript_text, video_title, channel_name, canonical_url