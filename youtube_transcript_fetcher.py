import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url_or_id: str) -> str:
    """
    Accepts a YouTube URL or bare ID and returns the video ID.
    Handles watch URLs, youtu.be links, shorts, etc.
    """
    url_or_id = url_or_id.strip()

    # Patterns for different YouTube URL styles
    patterns = [
        r"v=([\w-]+)",           # youtube.com/watch?v=ID
        r"youtu\.be/([\w-]+)",   # youtu.be/ID
        r"shorts/([\w-]+)",      # youtube.com/shorts/ID
    ]

    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)

    # Fallback: assume it's already an ID
    return url_or_id


def fetch_youtube_transcript(url_or_id: str) -> str:
    """
    Fetch English captions directly from YouTube and return them as plain text.
    Uses youtube-transcript-api. Raises a useful error if not available.
    """
    video_id = extract_video_id(url_or_id)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=["en", "en-US", "en-GB"]
        )
    except TranscriptsDisabled:
        raise RuntimeError("This video has transcripts disabled.")
    except NoTranscriptFound:
        raise RuntimeError("No transcripts found for this video.")
    except Exception as e:
        raise RuntimeError(f"Transcript fetch failed: {e}")

    text = " ".join(entry.get("text", "") for entry in transcript).replace("\n", " ").strip()

    if not text:
        raise RuntimeError("Transcript was empty.")

    return text