import datetime as dt
from typing import List, Dict

import requests

from config import require_env

# YouTube Data API v3 key (for search + stats)
YOUTUBE_API_KEY = require_env("YOUTUBE_API_KEY")

# Channels Leninware should watch. You can edit this list as needed.
CHANNELS = [
    "UCXIJgqnII2ZOINSWNOGFThA",  # Fox News
    "UC7yRILFFJ2zI_Ut9oZuDbWw",  # TYT
    "UCaXkIU1QidjPwiAYu6GcHjg",  # MeidasTouch
    "UCq16dvHk1FWk0TDvFu4CFOw",  # Brian Tyler Cohen (check / adjust if needed)
    "UCZJb0pVQF8l0Zo4QCXFvSrg",  # Beau of the Fifth Column
    "UCSPIZo7bGZpL8T3cHrIu9Kw",  # LegalEagle
]

SEARCH_API_URL = "https://www.googleapis.com/youtube/v3/search"


def fetch_channel_videos(channel_id: str, max_results: int = 10) -> list:
    """Fetch latest videos for a single channel using search.list.

    This is the main YouTube quota cost: each call is ~100 units.
    We do ONE call per channel per run.
    """
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": max_results,
        "type": "video",
    }

    resp = requests.get(SEARCH_API_URL, params=params, timeout=20)

    # Handle quota exceeded gracefully
    if resp.status_code == 403 and "quotaExceeded" in resp.text:
        print(f"[ingest] quotaExceeded when fetching channel {channel_id}")
        return []

    if resp.status_code != 200:
        print(f"[ingest] YouTube API error {resp.status_code} for {channel_id}: {resp.text[:200]}")
        return []

    data = resp.json()
    return data.get("items", [])


def get_recent_candidates(max_candidates: int = 40) -> List[Dict]:
    """Return a list of normalized candidate dicts from all configured channels.

    Each candidate looks like:
        {
            "video_id": str,
            "url": str,
            "title": str,
            "channel": str,
            "description": str,
            "published_at": datetime | None,
            "score": float,   # base score before virality worker
        }
    """
    all_items: List[Dict] = []

    for cid in CHANNELS:
        try:
            items = fetch_channel_videos(cid)
            all_items.extend(items)
        except Exception as e:
            print(f"[ingest] Failed to fetch for {cid}: {e}")

    candidates: List[Dict] = []

    for item in all_items:
        snippet = item.get("snippet", {})
        id_obj = item.get("id", {})
        video_id = id_obj.get("videoId")

        if not video_id:
            continue

        published_at_str = snippet.get("publishedAt")
        published_at = None
        if published_at_str:
            try:
                # Example: 2025-11-27T09:21:28Z
                published_at = dt.datetime.fromisoformat(
                    published_at_str.replace("Z", "+00:00")
                )
            except Exception:
                published_at = None

        candidate = {
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": snippet.get("title", "") or "",
            "channel": snippet.get("channelTitle", "") or "",
            "description": snippet.get("description", "") or "",
            "published_at": published_at,
            # Starting score – youtube_virality_worker will compute the real score.
            "score": 0.0,
        }
        candidates.append(candidate)

    # Newest videos first
    def _sort_key(c: Dict) -> dt.datetime:
        if c["published_at"] is None:
            # Oldest if unknown
            return dt.datetime.min.replace(tzinfo=dt.timezone.utc)
        return c["published_at"]

    candidates.sort(key=_sort_key, reverse=True)

    if max_candidates and len(candidates) > max_candidates:
        candidates = candidates[:max_candidates]

    print(f"[ingest] Found {len(candidates)} candidates")
    return candidates