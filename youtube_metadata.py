import re
import requests


def extract_video_id(url_or_id: str) -> str:
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        match = re.search(r"(v=|youtu\.be/)([\w-]+)", url_or_id)
        if match:
            return match.group(2)
    return url_or_id.strip()


def fetch_youtube_metadata(url_or_id: str) -> dict:
    """
    Returns:
        {
          "video_title": str or None,
          "channel_name": str or None,
          "video_url": str,
          "video_id": str
        }
    """
    video_id = extract_video_id(url_or_id)
    video_url = f"https://youtu.be/{video_id}"

    oembed_url = "https://www.youtube.com/oembed"
    params = {
        "url": video_url,
        "format": "json",
    }

    title = None
    channel_name = None

    try:
        resp = requests.get(oembed_url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            title = data.get("title")
            channel_name = data.get("author_name")
    except Exception:
        # If metadata fails, we just return None fields
        pass

    return {
        "video_title": title,
        "channel_name": channel_name,
        "video_url": video_url,
        "video_id": video_id,
    }