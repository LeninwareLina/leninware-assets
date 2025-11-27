import os
import sys
import json
import math
import datetime
import requests

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEOS_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"

# Default threshold for "good enough to process"
DEFAULT_THRESHOLD = 6.0


def _parse_published_at(published_at_str: str) -> datetime.datetime:
    """
    Parse an ISO 8601 publishedAt string into a UTC datetime.
    """
    # Examples: "2025-11-27T14:23:10Z"
    if not published_at_str:
        return datetime.datetime.utcnow()

    try:
        if published_at_str.endswith("Z"):
            published_at_str = published_at_str[:-1]
        return datetime.datetime.fromisoformat(published_at_str)
    except Exception:
        return datetime.datetime.utcnow()


def compute_score(snippet: dict, statistics: dict) -> float:
    """
    Compute a simple 0–10 virality score based on:
      - total views
      - view velocity (views per hour since publish)
      - like ratio
      - comment activity
      - recency penalty
    """

    now = datetime.datetime.utcnow()
    published_at_str = snippet.get("publishedAt") or ""
    published_dt = _parse_published_at(published_at_str)
    hours_since = max((now - published_dt).total_seconds() / 3600.0, 1.0)