import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url_or_id: str) -> str:
    """
    Accepts a YouTube URL or bare ID and returns the video ID.
    """
    url_or_id = url_or_id.strip()

    # Looks like a bare 11-char ID
    if len(url_or_id) == 11 and "/" not in url_or_id and "?" not in url_or_id:
        return url_or_id

    # Full URL
    match = re.search(r"(v=|youtu\.be/)([\w-]+)", url_or_id)
    if match:
        return match.group(2)

    # Fallback
    return url_or_id


def fetch_youtube_transcript(url_or_id: str) -> str:
    """
    Fetch English captions directly from YouTube and return them as plain text.
    Prefers auto/available track; if none exist, raises a descriptive error.
    """
    video_id = extract_video_id(url_or_id)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
    except TranscriptsDisabled:
        raise RuntimeError("This video has transcripts disabled.")
    except NoTranscriptFound:
        raise RuntimeError("No transcripts found for this video.")
    except Exception as e:
        raise RuntimeError(f"Transcript fetch failed: {e}")

    text = " ".join(entry.get("text", "") for entry in transcript)
    text = text.replace("\n", " ").strip()

    if not text:
        raise RuntimeError("Transcript was empty.")

    return text