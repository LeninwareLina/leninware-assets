from dataclasses import dataclass
from typing import Optional
import requests


OEMBED_URL = "https://www.youtube.com/oembed"


@dataclass
class YoutubeMetadata:
    title: Optional[str]
    channel_name: Optional[str]


def fetch_youtube_metadata(video_url: str) -> YoutubeMetadata:
    """
    Fetch basic metadata (title, channel name) using YouTube's oEmbed endpoint.
    """
    params = {
        "url": video_url,
        "format": "json",
    }

    try:
        resp = requests.get(OEMBED_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        # Fail soft — Leninware can still run with just the transcript.
        return YoutubeMetadata(title=None, channel_name=None)

    title = data.get("title")
    channel_name = data.get("author_name")
    return YoutubeMetadata(title=title, channel_name=channel_name)