import os
import json
from typing import List, Dict
import requests

# === Config ===

# YouTube Data API key (set this in Railway as YOUTUBE_API_KEY)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# File used to remember which videos we've already processed
SEEN_STATE_FILE = "youtube_seen.json"

# Add the channel IDs you want Leninware to monitor.
# For now, just put one or two. You can add more later.
#
# Example:
#   "UCd6Bw5Wxtxk7yQJkN7qDoYA"  # Secular Talk (example ID, replace with real one)
#
CHANNEL_IDS: List[str] = [
    "YOUR_FIRST_CHANNEL_ID_HERE",
    # "ANOTHER_CHANNEL_ID_HERE",
]


# === Internal helpers ===

def _ensure_api_key():
    if not YOUTUBE_API_KEY:
        raise RuntimeError(
            "YOUTUBE_API_KEY is not set. "
            "Add it as a service variable in Railway before running youtube_ingest."
        )


def _load_seen_ids() -> set:
    """Load set of already processed video IDs from disk."""
    try:
        with open(SEEN_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data)
    except FileNotFoundError:
        return set()
    except Exception:
        # If the file is corrupted, start fresh rather than crashing
        return set()


def _save_seen_ids(seen_ids: set) -> None:
    """Persist processed video IDs to disk."""
    try:
        with open(SEEN_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(list(seen_ids)), f)
    except Exception as e:
        # Not fatal for the pipeline; just log to stdout.
        print(f"[youtube_ingest] Warning: failed to save seen IDs: {e}")


def _fetch_channel_latest_videos(channel_id: str, max_results: int = 5) -> List[Dict]:
    """
    Fetch the most recent YouTube videos for a given channel.
    Returns a list of dicts with video_id, url, title, published_at.
    """
    _ensure_api_key()

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "type": "video",
        "maxResults": max_results,
    }

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    items: List[Dict] = []
    for item in data.get("items", []):
        vid = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})
        if not vid:
            continue

        items.append(
            {
                "video_id": vid,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "title": snippet.get("title", ""),
                "published_at": snippet.get("publishedAt", ""),
                "channel_id": channel_id,
                "channel_title": snippet.get("channelTitle", ""),
            }
        )

    return items


# === Public entrypoint ===

def fetch_new_videos(max_per_channel: int = 5) -> List[Dict]:
    """
    Fetch new (not-yet-seen) videos from all configured CHANNEL_IDS.

    Returns a list of dicts:
        {
          "video_id": ...,
          "url": ...,
          "title": ...,
          "published_at": ...,
          "channel_id": ...,
          "channel_title": ...
        }

    Also updates youtube_seen.json so the same videos aren't processed twice.
    """
    if not CHANNEL_IDS:
        raise RuntimeError(
            "youtube_ingest.CHANNEL_IDS is empty. "
            "Edit youtube_ingest.py and add at least one channel ID."
        )

    seen_ids = _load_seen_ids()
    new_videos: List[Dict] = []

    for channel_id in CHANNEL_IDS:
        try:
            videos = _fetch_channel_latest_videos(
                channel_id=channel_id,
                max_results=max_per_channel,
            )
        except Exception as e:
            print(f"[youtube_ingest] Error fetching for channel {channel_id}: {e}")
            continue

        for v in videos:
            vid = v["video_id"]
            if vid not in seen_ids:
                new_videos.append(v)
                seen_ids.add(vid)

    if new_videos:
        _save_seen_ids(seen_ids)

    # Sort newest → oldest by published_at just to be tidy
    new_videos.sort(key=lambda v: v.get("published_at", ""), reverse=True)
    return new_videos


# Simple manual test: run `python youtube_ingest.py` on Railway or locally
if __name__ == "__main__":
    print("=== Leninware YouTube Ingest Test ===")
    try:
        vids = fetch_new_videos(max_per_channel=3)
    except Exception as e:
        print("Error:", e)
    else:
        if not vids:
            print("No new videos found (or CHANNEL_IDS is still using placeholders).")
        else:
            for v in vids:
                print(
                    f"- [{v['channel_title']}] {v['title']}\n"
                    f"  {v['url']}\n"
                )