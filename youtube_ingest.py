# youtube_ingest.py

import datetime as dt
from typing import List, Dict, Any

import requests

from config import YOUTUBE_API_KEY, require_env

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


# You can adjust these to your chosen channels
CHANNEL_IDS = [
    # "UC..."  # MeidasTouch
    # "UC..."  # Secular Talk
    # etc...
]


def _iso_to_dt(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def get_candidate_videos(max_per_feed: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch a small list of recent videos from configured channel IDs.
    Returns a list of dicts with url, title, channel, stats, etc.
    """
    require_env("YOUTUBE_API_KEY", YOUTUBE_API_KEY)
    if not CHANNEL_IDS:
        print("[youtube_ingest] No CHANNEL_IDS configured, returning empty list.")
        return []

    videos: List[Dict[str, Any]] = []

    for channel_id in CHANNEL_IDS:
        # 1) search for recent videos
        search_params = {
            "part": "snippet",
            "channelId": channel_id,
            "order": "date",
            "type": "video",
            "maxResults": max_per_feed,
            "key": YOUTUBE_API_KEY,
        }
        s_resp = requests.get(f"{YOUTUBE_API_BASE}/search", params=search_params, timeout=20)
        if s_resp.status_code != 200:
            print(f"[youtube_ingest] search error {s_resp.status_code}: {s_resp.text[:200]}")
            continue

        search_data = s_resp.json()
        video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
        if not video_ids:
            continue

        # 2) get stats
        stats_params = {
            "part": "statistics,snippet",
            "id": ",".join(video_ids),
            "key": YOUTUBE_API_KEY,
        }
        v_resp = requests.get(f"{YOUTUBE_API_BASE}/videos", params=stats_params, timeout=20)
        if v_resp.status_code != 200:
            print(f"[youtube_ingest] videos error {v_resp.status_code}: {v_resp.text[:200]}")
            continue

        v_data = v_resp.json()
        for item in v_data.get("items", []):
            vid = item["id"]
            snippet = item["snippet"]
            stats = item.get("statistics", {})

            videos.append(
                {
                    "video_id": vid,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "title": snippet.get("title", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "published_at": _iso_to_dt(snippet.get("publishedAt", dt.datetime.now(dt.timezone.utc).isoformat())),
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                }
            )

    return videos