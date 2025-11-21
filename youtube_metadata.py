import re
import requests


def extract_video_id(url_or_id: str) -> str:
    """
    Accepts a YouTube URL or bare ID and returns the video ID.
    """
    url_or_id = url_or_id.strip()

    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        match = re.search(r"(v=|youtu\.be/)([\w-]+)", url_or_id)
        if match:
            return match.group(2)
    return url_or_id


def get_youtube_metadata(url_or_id: str) -> dict:
    """
    Uses YouTube's public oEmbed endpoint to get title + channel.
    No API key required.
    """
    video_id = extract_video_id(url_or_id)
    full_url = f"https://www.youtube.com/watch?v={video_id}"

    oembed_url = f"https://www.youtube.com/oembed?url={full_url}&format=json"
    resp = requests.get(oembed_url, timeout=10)

    if resp.status_code != 200:
        raise RuntimeError(f"Metadata fetch failed with status {resp.status_code}")

    data = resp.json()

    return {
        "video_title": data.get("title") or "",
        "channel_name": data.get("author_name") or "",
        "video_url": full_url,
    }