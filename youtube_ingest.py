import datetime as dt
from typing import List, Dict

import requests

from config import YOUTUBE_API_KEY

# Channels Leninware originally pulled from. These came from your old repo.
CHANNELS = [
    "UCXIJgqnII2ZOINSWNOGFThA",  # Fox News
    "UC7yRILFFJ2zI_Ut9oZuDbWw",  # TYT
    "UC6TmAlx4q_GU8Z1LENzOdJw",  # Misc news
    "UCaXkIU1QidjPwiAYu6GcHjg",  # MeidasTouch
    "UCq16dvHk1FWk0TDvFu4CFOw",  # Brian Tyler Cohen
    "UCZJb0pVQF8l0Zo4QCXFvSrg",  # Beau of the Fifth Column
    "UCSPIZo7bGZpL8T3cHrIu9Kw",  # LegalEagle
]

API_URL = "https://www.googleapis.com/youtube/v3/search"


def fetch_channel_videos(channel_id: str) -> list:
    """
    Return a list of raw video items from a YouTube channel.

    This makes ONE search.list call per channel (~100 quota units).
    """
    if not YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is not set in config / environment")

    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 20,
        "type": "video",
    }

    resp = requests.get(API_URL, params=params, timeout=20)

    # If quota is exceeded, bail with a clear error instead of spamming retries.
    if resp.status_code == 403 and "quotaExceeded" in resp.text:
        raise RuntimeError(f"YoutubeAPI quotaExceeded for channel {channel_id}: {resp.text}")

    if resp.status_code != 200:
        raise RuntimeError(f"YoutubeAPI 403/400: {resp.text}")

    return resp.json().get("items", [])


def get_candidate_videos() -> list:
    """
    Fetch videos from all configured channels and flatten list.
    Returns raw YouTube API items.
    """
    all_items = []

    for cid in CHANNELS:
        try:
            items = fetch_channel_videos(cid)
            all_items.extend(items)
        except Exception as e:
            print(f"[ingest] Failed to fetch for {cid}: {e}")

    return all_items


def get_recent_candidates(max_candidates: int = 40) -> List[Dict]:
    """
    Wrapper used by youtube_virality_worker.run_virality_pass().

    Turns raw YouTube API items into a simple list of candidate dicts:
    {
        'video_id': str,
        'url': str,
        'title': str,
        'channel': str,
        'description': str,
        'published_at': datetime | None,
        'score': float,          # base score (LLM will overwrite)
    }
    """
    raw_items = get_candidate_videos()
    candidates: List[Dict] = []

    for item in raw_items:
        snippet = item.get("snippet", {})
        id_obj = item.get("id", {})
        video_id = id_obj.get("videoId")

        if not video_id:
            continue

        published_at_str = snippet.get("publishedAt")
        published_at = None
        if published_at_str:
            try:
                # "2025-11-27T09:21:28Z" → aware datetime
                published_at = dt.datetime.fromisoformat(
                    published_at_str.replace("Z", "+00:00")
                )
            except Exception:
                published_at = None

        candidate = {
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "description": snippet.get("description", ""),
            "published_at": published_at,
            # Starting score – youtube_virality_worker will compute the real score
            "score": 0.0,
        }
        candidates.append(candidate)

    # Newest videos first, if we have timestamps
    def _sort_key(c):
        if c["published_at"] is None:
            # Ancient past if unknown, so they end up last
            return dt.datetime.min.replace(tzinfo=dt.timezone.utc)
        return c["published_at"]

    candidates.sort(key=_sort_key, reverse=True)

    if max_candidates and len(candidates) > max_candidates:
        candidates = candidates[:max_candidates]

    print(f"[worker] Found {len(candidates)} candidates")
    return candidates