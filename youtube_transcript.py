from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
)


def _extract_video_id(url_or_id: str) -> str:
    """
    Accepts a YouTube URL or bare ID and returns the video ID.
    """
    url_or_id = url_or_id.strip()

    # Looks like a bare 11-char ID
    if len(url_or_id) == 11 and "/" not in url_or_id and "?" not in url_or_id:
        return url_or_id

    parsed = urlparse(url_or_id)

    # youtu.be/VIDEOID
    if parsed.hostname and "youtu.be" in parsed.hostname:
        return parsed.path.lstrip("/")

    # youtube.com/watch?v=VIDEOID
    if parsed.hostname and "youtube.com" in parsed.hostname:
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]

    raise ValueError("Could not extract a YouTube video ID from that input.")


def fetch_youtube_transcript(url_or_id: str) -> str:
    """
    Fetch English captions directly from YouTube and return them as plain text.
    Prefers human captions, falls back to auto-generated.
    """
    video_id = _extract_video_id(url_or_id)

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise RuntimeError("No transcripts found for this video.")
    except Exception as e:
        raise RuntimeError(f"Failed to list transcripts: {e}")

    transcript = None

    # Try human-made English captions first
    for langs in (["en", "en-US", "en-GB"], ["en"]):
        try:
            transcript = transcript_list.find_manually_created_transcript(langs)
            break
        except Exception:
            continue

    # Fall back to auto-generated
    if transcript is None:
        for langs in (["en", "en-US", "en-GB"], ["en"]):
            try:
                transcript = transcript_list.find_generated_transcript(langs)
                break
            except Exception:
                continue

    if transcript is None:
        raise RuntimeError("No English transcript (manual or auto) is available.")

    chunks = transcript.fetch()
    pieces = []
    for chunk in chunks:
        text = chunk.get("text", "").replace("\n", " ").strip()
        if text:
            pieces.append(text)

    if not pieces:
        raise RuntimeError("Transcript was empty.")

    return " ".join(pieces)