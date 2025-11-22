# youtube_ingest.py
"""
Fetches candidate videos from YouTube channels using the YouTube Data API.

Returns a list of dicts:
{
    "title": str,
    "url": str,
    "channel": str,
    "published_at": datetime,
    "view_count": int,
    "like_count": int,
    "comment_count": int
}
"""

import os
import datetime as dt
import requests
from typing import List, Dict, Any

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Add whatever channels you want here
CHANNEL_IDS = [
    "UC1yBKRuGpC1tSM73A0ZjYjQ",  # Secular Talk
    "UCJtKw3hNUnj_lQj7A5zE2fw",  # Majority Report
    "UCUpMJwMqE9a-YA_aO0RM8Kw",  # MeidasTouch
    "UC16niRr50-MSBwiO3YDb3RA",  # BBC News
]


def yt_get(endpoint: str, params: dict) -> dict:
    base = "https://www.googleapis.com/youtube/v3/"
    params["key"] = YOUTUBE_API_KEY
    r = requests.get(base + endpoint, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def get_uploads_playlist(channel_id: str) -> str:
    data = yt_get("channels", {"part": "contentDetails", "id": channel_id})
    return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_playlist_items(playlist_id: str, max_items=10) -> List[Dict[str, Any]]:
    data = yt_get(
        "playlistItems",
        {"part": "snippet,contentDetails", "playlistId": playlist_id, "maxResults": max_items},
    )
    return data["items"]


def get_video_stats(video_id: str) -> Dict[str, int]:
    data = yt_get("videos", {"part": "statistics", "id": video_id})
    stats = data["items"][0]["statistics"]
    return {
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
    }


def get_candidate_videos(max_per_feed=10) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for cid in CHANNEL_IDS:
        try:
            uploads = get_uploads_playlist(cid)
            items = get_playlist_items(uploads, max_per_feed)

            for item in items:
                vid = item["contentDetails"]["videoId"]
                snippet = item["snippet"]

                stats = get_video_stats(vid)

                published = dt.datetime.fromisoformat(
                    snippet["publishedAt"].replace("Z", "+00:00")
                )

                results.append(
                    {
                        "title": snippet["title"],
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "channel": snippet["channelTitle"],
                        "published_at": published,
                        **stats,
                    }
                )
        except Exception as e:
            print(f"[ingest] Error fetching channel {cid}: {e}")

    return results