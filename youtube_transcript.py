from youtube_transcript_api import YouTubeTranscriptApi
import re


def extract_video_id(url_or_id: str) -> str:
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        match = re.search(r"(v=|youtu\.be/)([\w-]+)", url_or_id)
        if match:
            return match.group(2)
    return url_or_id


def fetch_youtube_transcript(url_or_id: str) -> str:
    video_id = extract_video_id(url_or_id)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    text = " ".join([entry["text"] for entry in transcript])
    return text