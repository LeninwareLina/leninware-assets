# youtube_ingest.py
"""
Fetch recent videos from a set of channels using their RSS feeds,
then enrich them with stats from the YouTube Data API v3.

This module is read-only: it never uploads or changes anything on YouTube.
"""

import os
import datetime as dt
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs

import feedparser
import requests

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    print("[youtube_ingest] WARNING: YOUTUBE_API_KEY is not set; "
          "stats lookups will fail.")


# === Configure target channels here =========================================

# TODO: put the real channel IDs you care about.
# You can grab them from the channel URL:
#   https://www.youtube.com/channel/UCxxxx -> channel_id is the UCxxxx part
CHANNEL_FEEDS: Dict[str, str] = {
    "Secular Talk": "https://www.youtube.com/feeds/videos.xml?channel_id=REPLACE_ME",
    "BBC News": "https://www.youtube.com/feeds/videos.xml?channel_id=REPLACE_ME",
    "CNN": "https://www.youtube.com/feeds/videos.xml?channel_id=REPLACE_ME",
    "MeidasTouch": "https://www.youtube.com/feeds/videos.xml?channel_id=REPLACE_ME",
    "Majority Report": "https://www.youtube.com/feeds/videos.xml?channel_id=REPLACE_ME",
}


# === Helpers ================================================================

def _extract_video_id_from_url(url: str) -> str | None:
    """Best-effort extraction of a YouTube video ID from a URL."""
    if not url:
        return None

    parsed = urlparse(url)

    # Short links: https://youtu.be/VIDEO_ID
    if parsed.netloc in {"youtu.be", "www.youtu.be"}:
        return parsed.path.lstrip("/") or None

    # Normal watch URLs: https://www.youtube.com/watch?v=VIDEO_ID
    qs = parse_qs(parsed.query)
    if "v" in qs and qs["v"]:
        return qs["v"][0]

    return None


def _published_to_datetime(entry) -> dt.datetime:
    """Convert feedparser's published field into an aware datetime."""
    # feedparser gives published_parsed as time.struct_time
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        t = entry.published_parsed
        return dt.datetime(
            t.tm_year,
            t.tm_mon,
            t.tm_mday,
            t.tm_hour,
            t.tm_min,
            t.tm_sec,
            tzinfo=dt.timezone.utc,
        )
    # Fallback: now
    return dt.datetime.now(dt.timezone.utc)


# === Public API =============================================================

def fetch_recent_from_feeds(max_per_feed: int = 10) -> List[Dict[str, Any]]:
    """
    Pull recent videos from each configured RSS feed.

    Returns a list of dicts:
        {
            "channel": str,
            "title": str,
            "url": str,
            "video_id": str,
            "published_at": datetime,
        }
    """
    items: List[Dict[str, Any]] = []

    for channel, feed_url in CHANNEL_FEEDS.items():
        print(f"[youtube_ingest] Fetching feed for {channel}: {feed_url}")
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:max_per_feed]:
            link = getattr(entry, "link", "")
            video_id = getattr(entry, "yt_videoid", None) or _extract_video_id_from_url(
                link
            )

            if not video_id:
                print(f"[youtube_ingest] Could not extract video id for entry: {link}")
                continue

            items.append(
                {
                    "channel": channel,
                    "title": getattr(entry, "title", "").strip(),
                    "url": link,
                    "video_id": video_id,
                    "published_at": _published_to_datetime(entry),
                }
            )

    print(f"[youtube_ingest] Collected {len(items)} recent videos from feeds.")
    return items


def enrich_with_stats(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    For each video dict (must contain 'video_id'), attach basic statistics
    from YouTube Data API.

    Adds keys:
        view_count, like_count, comment_count
    """
    if not videos:
        return []

    if not YOUTUBE_API_KEY:
        print("[youtube_ingest] No YOUTUBE_API_KEY; returning videos without stats.")
        # still return original list so the rest of the pipeline can run in a basic way
        return videos

    url = "https://www.googleapis.com/youtube/v3/videos"

    # API supports up to 50 IDs per call; we'll keep it simple and do one by one.
    for v in videos:
        vid = v["video_id"]
        params = {
            "part": "statistics",
            "id": vid,
            "key": YOUTUBE_API_KEY,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            if not items:
                print(f"[youtube_ingest] No stats for {vid}")
                continue

            stats = items[0].get("statistics", {})
            v["view_count"] = int(stats.get("viewCount", 0))
            v["like_count"] = int(stats.get("likeCount", 0))
            v["comment_count"] = int(stats.get("commentCount", 0))
        except Exception as e:
            print(f"[youtube_ingest] Error fetching stats for {vid}: {e}")

    return videos


def get_candidate_videos(max_per_feed: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience: fetch from RSS feeds and enrich with stats in one call.
    """
    base = fetch_recent_from_feeds(max_per_feed=max_per_feed)
    return enrich_with_stats(base)


if __name__ == "__main__":
    # quick manual test
    vids = get_candidate_videos(max_per_feed=3)
    for v in vids:
        print(
            f"{v['channel']} | {v['title']} | views={v.get('view_count')} "
            f"likes={v.get('like_count')} comments={v.get('comment_count')}"
        )