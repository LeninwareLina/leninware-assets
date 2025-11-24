# youtube_ingest.py

import datetime as dt
from typing import List, Dict, Any

import requests

from config import YOUTUBE_API_KEY, require_env


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


# You can adjust these to your chosen channels
CHANNEL_IDS = [
    # === Liberal/Progressive Commentary ===
    "UC9r9HYFxEQOBXSopFS61ZWg",  # MeidasTouch
    "UCvixJtaXuBC8RQfF_vhWEfg",  # David Pakman (Pakman Clips)
    "UCNysHmvn8TME2jQu57j66_A",  # More Perfect Union
    "UCPWXiRWZ29zrxPFIQT7eHSA",  # Brian Tyler Cohen
    
    # === Conservative/Culture War ===
    "UCL_f53ZEJxp8TtlOkHwMV9Q",  # Jordan Peterson  
    "UCIeLsbFRTTg_BdPgmNp4lNg",  # Tim Pool (Timcast)
    
    # === Leftist Commentary ===
    "UC554eY5jNUfDq3yDOJYirOQ",  # HasanAbi
    "UCyUo8SJqSdF_PSz5B_HBKNQ",  # H3H3 (h3h3Productions)
]
def _iso_to_dt(s: str) -> dt.datetime:
    """Helper to parse ISO datetime string"""
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def get_candidate_videos(max_per_feed: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch a small list of recent videos from configured channel IDs.
    Returns a list of dicts with url, title, channel, stats, etc.
    """
    require_env("YOUTUBE_API_KEY", YOUTUBE_API_KEY)
    
    if not CHANNEL_IDS:
        print("[youtube_ingest] No CHANNEL_IDS configured, returning empty.")
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
        s_resp = requests.get(f"{YOUTUBE_API_BASE}/search", params=search_params)
        if s_resp.status_code != 200:
            print(f"[youtube_ingest] search error ({s_resp.status_code})")
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
        v_resp = requests.get(f"{YOUTUBE_API_BASE}/videos", params=stats_params)
        if v_resp.status_code != 200:
            print(f"[youtube_ingest] videos error ({v_resp.status_code})")
            continue

        v_data = v_resp.json()
        for item in v_data.get("items", []):
            vid = item["id"]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})

            videos.append({
                "video_id": vid,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "published_at": _iso_to_dt(snippet.get("publishedAt")),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
            })

    return videos
