# youtube_ingest.py

import re
from pathlib import Path
from typing import List, Dict
import requests

from config import YOUTUBE_API_KEY

CHANNELS_FILE = Path("prompts/youtube_channels.txt")

CHANNEL_URL_RE = re.compile(r"/channel/([A-Za-z0-9_-]+)")


def load_channel_ids() -> List[str]:
    if not CHANNELS_FILE.exists():
        raise FileNotFoundError(
            f"Missing channel list: {CHANNELS_FILE}"
        )

    ids = []
    for raw in CHANNELS_FILE.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = CHANNEL_URL_RE.search(line)
        if m:
            ids.append(m.group(1))
        else:
            ids.append(line)
    return ids


def _get_video_duration(video_id: str) -> int:
    """
    Returns video duration in seconds.
    Returns 0 for Shorts or unknown.
    """
    url = (
        "https://www.googleapis.com/youtube/v3/videos"
        f"?key={YOUTUBE_API_KEY}"
        f"&part=contentDetails"
        f"&id={video_id}"
    )

    resp = requests.get(url).json()
    items = resp.get("items", [])
    if not items:
        return 0

    iso = items[0]["contentDetails"]["duration"]
    # Convert ISO-8601 duration (PT#M#S) to seconds
    # Example: PT12S, PT1M12S, PT2M.
    import isodate
    try:
        duration = isodate.parse_duration(iso).total_seconds()
        return int(duration)
    except:
        return 0


def get_recent_candidates(max_results: int = 5) -> List[Dict]:
    """
    Fetches only NORMAL videos (no Shorts).
    Returns list of dictionaries with video metadata.
    """

    channel_ids = load_channel_ids()
    candidates = []

    for channel_id in channel_ids:
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?key={YOUTUBE_API_KEY}"
            f"&channelId={channel_id}"
            "&part=snippet"
            "&order=date"
            f"&maxResults={max_results}"
        )

        resp = requests.get(url).json()
        items = resp.get("items", [])
        for item in items:
            if item["id"]["kind"] != "youtube#video":
                continue

            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel = item["snippet"]["channelTitle"]
            url = f"https://www.youtube.com/watch?v={video_id}"

            # Filter Shorts by duration
            dur_s = _get_video_duration(video_id)
            if dur_s < 60:
                print(f"[ingest] Skipping short: '{title}' ({dur_s}s)")
                continue

            candidates.append(
                {
                    "video_id": video_id,
                    "title": title,
                    "channel": channel,
                    "duration_s": dur_s,
                    "url": url,
                }
            )

    return candidates