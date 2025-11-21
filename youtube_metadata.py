import re
import requests
from bs4 import BeautifulSoup


def extract_video_id(url_or_id: str) -> str:
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
    video_id = extract_video_id(url_or_id)
    url = f"https://www.youtube.com/watch?v={video_id}"

    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    title_tag = soup.find("meta", property="og:title")
    channel_tag = soup.find("link", itemprop="name")

    video_title = title_tag["content"] if title_tag else "Unknown Title"
    channel_name = channel_tag["content"] if channel_tag else "Unknown Channel"

    return {
        "video_title": video_title,
        "channel_name": channel_name,
        "video_url": url,
    }