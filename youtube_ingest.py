# youtube_ingest.py
"""
Fetches candidate videos from YouTube channels using RSS + YouTube Data API.

Output format for each video:
{
    "title": str,
    "channel": str,
    "url": str,
    "video_id": str,
    "published_at": datetime,
    "view_count": int,
    "like_count": int,
    "comment_count": int
}
"""

import os
import datetime as dt
from typing import List, Dict, Any

import requests
import xml.etree.ElementTree as ET


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# === YOUR CHANNEL RSS FEEDS ====================================================
# Add/remove channels here (RSS format is stable, safe, and requires NO auth)
RSS_FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCldfgbzNILYZA4dmDt4Cd6A",  # Secular Talk
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCxICcwYRM4Yf6cZTt9mE2Zw",  # Majority Report
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCupvZG-5ko_eiXAupbDfxWw",  # CNN
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCaXkIU1QidjPwiAYu6GcHjg",  # BBC
]

# ==============================================================================


def fetch_rss_entries(feed_url: str, max_items: int) -> List[Dict[str, Any]]:
    """Parse a YouTube RSS feed and extract video entries."""
    resp = requests.get(feed_url, timeout=20)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    ns = {"yt": "http://www.youtube.com/xml/schemas/2015", "atom": "http://www.w3.org/2005/Atom"}

    items = []
    for entry in root.findall("atom:entry", ns)[:max_items]:
        video_id = entry.find("yt:videoId", ns).text
        title = entry.find("atom:title", ns).text
        channel = entry.find("atom:author/atom:name", ns).text
        published = entry.find("atom:published", ns).text

        # convert timestamp
        published_dt = dt.datetime.fromisoformat(published.replace("Z", "+00:00"))

        items.append(
            {
                "title": title,
                "channel": channel,
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "published_at": published_dt,
            }
        )

    return items


def fetch_video_stats(video_id: str) -> Dict[str, int]:
    """Use YouTube Data API (simple API key) to get public stats."""
    if not YOUTUBE_API_KEY:
        return {"view_count": 0, "like_count": 0, "comment_count": 0}

    endpoint = "https://www.googleapis.com/youtube/v3/videos"

    params = {
        "id": video_id,
        "part": "statistics",
        "key": YOUTUBE_API_KEY,
    }

    resp = requests.get(endpoint, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    try:
        stats = data["items"][0]["statistics"]
        return {
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
        }
    except Exception:
        return {"view_count": 0, "like_count": 0, "comment_count": 0}


def get_candidate_videos(max_per_feed: int = 10) -> List[Dict[str, Any]]:
    """
    Main entry point for the virality worker.
    Returns all videos enriched with YouTube stats.
    """
    all_videos = []

    for feed in RSS_FEEDS:
        try:
            entries = fetch_rss_entries(feed, max_items=max_per_feed)
            for v in entries:
                stats = fetch_video_stats(v["video_id"])
                v.update(stats)
                all_videos.append(v)

        except Exception as e:
            print(f"[youtube_ingest] Error fetching: {feed} → {e}")

    return all_videos