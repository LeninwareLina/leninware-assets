# youtube_ingest.py

from typing import List, Dict, Any
import requests

from config import require_env, YOUTUBE_API_BASE


# Channels to ingest (restored + your channel)
CHANNEL_IDS = [
    "UCXIJgqnII2ZOINSWNOGFThA",  # Fox News
    "UC3XTzVzaHQEd30rQbuvCtTQ",  # MSNBC
    "UCY8p5PCLuLhqZ4Lf37jHwoA",  # MeidasTouch
    "UCnrj9Zf2HNNadUx1y7t9dVQ",  # Brian Tyler Cohen
    "UCfRqyGJ_1N41q0p6jFJwaLg",  # The Hill (Rising)
    "UCYO_jab_esuFRV4b17AJtAw",  # Vox
    "UCb8Rde3uRL0JLZ8ZzE1zE7w",  # TYT
    "UCSm7JPn2xvLCGq53_wXA0Hg",  # Secular Talk

    # Your channel for debugging/self-analysis
    "UCtxBVxXhuIjsxajIgUi01pg",  # LeninwareAI
]

SEARCH_API = f"{YOUTUBE_API_BASE}/search"
VIDEOS_API = f"{YOUTUBE_API_BASE}/videos"


def get_candidate_videos() -> List[Dict[str, Any]]:
    """
    Fetch the latest videos from each configured YouTube channel ID.

    Returns a list of dicts:
        {
            "url": str,
            "title": str,
            "channel": str,
            "views": int,
            "likes": int,
            "comments": int,
        }
    """
    api_key = require_env("YOUTUBE_API_KEY")

    candidates: List[Dict[str, Any]] = []
    print("[ingest] Fetching videos from configured channels...")

    for cid in CHANNEL_IDS:
        try:
            # Most recent uploads by date
            search_resp = requests.get(
                SEARCH_API,
                params={
                    "part": "snippet",
                    "channelId": cid,
                    "maxResults": 3,
                    "order": "date",
                    "type": "video",
                    "key": api_key,
                },
                timeout=20,
            )
            search_resp.raise_for_status()
            search_data = search_resp.json()

            for item in search_data.get("items", []):
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]

                # Fetch stats for each video
                stats_resp = requests.get(
                    VIDEOS_API,
                    params={
                        "part": "statistics",
                        "id": video_id,
                        "key": api_key,
                    },
                    timeout=20,
                )
                stats_resp.raise_for_status()
                stats_data = stats_resp.json()

                stats = stats_data["items"][0]["statistics"]

                candidates.append(
                    {
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "title": snippet["title"],
                        "channel": snippet["channelTitle"],
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0)),
                    }
                )

        except Exception as e:
            print(f"[ingest] Failed to fetch for channel {cid}: {e}")

    print(f"[ingest] Found {len(candidates)} total videos.")
    return candidates