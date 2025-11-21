import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url_or_id: str) -> str:
    # Handles ?v=, youtu.be/, shorts/, etc
    patterns = [
        r"v=([\w-]+)",
        r"youtu\.be/([\w-]+)",
        r"shorts/([\w-]+)",
    ]

    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)

    return url_or_id


def fetch_youtube_transcript(url_or_id: str) -> str:
    video_id = extract_video_id(url_or_id)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    text = " ".join([entry["text"] for entry in transcript])
    return text