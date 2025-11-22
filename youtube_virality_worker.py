# youtube_virality_worker.py

import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Any

import requests

from leninware_video_pipeline import generate_leninware_tts_from_url


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY is not set")

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


# ------------------------------------------------------------
# CHANNELS YOU REQUESTED
# ------------------------------------------------------------
CHANNEL_IDS: List[str] = [
    "UCQbvDssDPhVsaQUNbQZzX7A",  # MeidasTouch
    "UCupvZG-5ko_eiXAUPK3gY_g",  # CNN
    "UCldfgbzNILYZA4dmDt4Cd6A",  # Secular Talk
    "UCp4-hM87FDgXfO3TtR1x68Q",  # The Majority Report
    "UC16niRr50-MSBwiO3YDb3RA",  # BBC News
]

# Virality threshold (tune as needed)
VIRALITY_THRESHOLD = 7.5

# Number of recent videos to inspect per channel
MAX_RECENT_VIDEOS = 10


# ------------------------------------------------------------
# YOUTUBE HELPERS
# ------------------------------------------------------------

def youtube_get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    params = dict(params)
    params["key"] = YOUTUBE_API_KEY
    resp = requests.get(f"{YOUTUBE_API_BASE}/{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_recent_videos(channel_id: str, max_results: int = MAX_RECENT_VIDEOS) -> List[Dict[str, Any]]:
    search = youtube_get(
        "search",
        {
            "part": "id,snippet",
            "channelId": channel_id,
            "maxResults": max_results,
            "order": "date",
            "type": "video",
        },
    )

    items = search.get("items", [])
    if not items:
        return []

    video_ids = [item["id"]["videoId"] for item in items]

    videos_resp = youtube_get(
        "videos",
        {"part": "snippet,statistics", "id": ",".join(video_ids)},
    )

    results = []
    for item in videos_resp.get("items", []):
        snippet = item["snippet"]
        stats = item.get("statistics", {})

        results.append(
            {
                "video_id": item["id"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "published_at": snippet.get("publishedAt"),
                "statistics": {
                    "viewCount": int(stats.get("viewCount", 0)),
                    "likeCount": int(stats.get("likeCount", 0)),
                    "commentCount": int(stats.get("commentCount", 0)),
                },
            }
        )

    return results


# ------------------------------------------------------------
# VIRALITY SCORING
# ------------------------------------------------------------

HOT_KEYWORDS = [
    "trump", "donald",
    "biden",
    "israel", "gaza", "palestine",
    "war", "genocide", "ceasefire",
    "election",
    "fascist",
    "ai",
    "billionaire",
    "strike",
    "protest",
    "riot",
]

def hours_since(timestamp: str) -> float:
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    delta = datetime.now(timezone.utc) - dt
    return max(delta.total_seconds() / 3600, 0.01)

def keyword_score(title: str, desc: str) -> float:
    text = (title + " " + desc).lower()
    hits = sum(1 for kw in HOT_KEYWORDS if kw in text)
    return min(hits, 5.0)

def engagement_score(stats: Dict[str, int]) -> float:
    views = max(stats.get("viewCount", 1), 1)
    likes = stats.get("likeCount", 0)
    comments = stats.get("commentCount", 0)
    rate = (likes + 2 * comments) / views
    return min(rate * 40.0, 4.0)

def velocity_score(stats: Dict[str, int], age_hours: float) -> float:
    vph = stats["viewCount"] / max(age_hours, 0.25)
    if vph <= 500: return 1.0
    if vph <= 2000: return 3.0
    if vph <= 5000: return 6.0
    if vph <= 10000: return 8.0
    return 10.0

def virality(video: Dict[str, Any]) -> float:
    stats = video["statistics"]
    age = hours_since(video["published_at"])
    k = keyword_score(video["title"], video["description"])
    e = engagement_score(stats)
    v = velocity_score(stats, age)
    return round(0.4 * v + 0.35 * e + 0.25 * k, 2)


# ------------------------------------------------------------
# MAIN WORKER
# ------------------------------------------------------------

def run_once():
    for channel_id in CHANNEL_IDS:
        print(f"\n=== Checking channel {channel_id} ===")
        vids = fetch_recent_videos(channel_id)
        if not vids:
            print("No recent videos.")
            continue

        for vid in vids:
            score = virality(vid)
            url = f"https://www.youtube.com/watch?v={vid['video_id']}"

            print(f"\nTitle: {vid['title']}")
            print(f"URL:   {url}")
            print(f"Score: {score}")

            if score >= VIRALITY_THRESHOLD:
                print(">> VIRAL: sending to Leninware Sonnet-4...\n")
                try:
                    script = generate_leninware_tts_from_url(url)
                    print("====== LENINWARE OUTPUT ======\n")
                    print(script)
                    print("\n==============================\n")
                except Exception as e:
                    print(f"Leninware pipeline error: {e}")
            else:
                print("Not viral enough.")

if __name__ == "__main__":
    run_once()