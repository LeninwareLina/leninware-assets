import re
import requests


def extract_video_id(url_or_id: str) -> str:
    """
    Accepts a YouTube URL or bare ID and returns the video ID.
    """
    url_or_id = url_or_id.strip()

    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
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


def fetch_youtube_metadata(url_or_id: str) -> dict:
    """
    Uses YouTube's oEmbed endpoint to get title + channel.
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