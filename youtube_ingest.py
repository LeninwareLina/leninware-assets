# youtube_ingest.py

import re
from pathlib import Path
from typing import List

from config import YOUTUBE_API_KEY
import requests


CHANNELS_FILE = Path("prompts/youtube_channels.txt")

CHANNEL_URL_RE = re.compile(r"/channel/([A-Za-z0-9_-]+)")


def load_channel_ids() -> List[str]:
    """
    Load channel IDs from prompts/youtube_channels.txt

    Format:
        UC1234567890abcdef
        https://youtube.com/channel/UCabcdef...
        # comments allowed
    """
    if not CHANNELS_FILE.exists():
        raise FileNotFoundError(
            f"Missing channel list: {CHANNELS_FILE}. "
            "Create it with one channel per line."
        )

    ids = []

    for raw in CHANNELS_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        m = CHANNEL_URL_RE.search(line)
        if m:
            ids.append(m.group(1))
        else:
            ids.append(line)

    return ids


def get_recent_candidates(max_results: int = 5) -> List[dict]:
    """
    For each channel in youtube_channels.txt,
    fetch recent videos.
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

        resp = requests.get(url)
        data = resp.json()

        for item in data.get("items", []):
            if item["id"]["kind"] != "youtube#video":
                continue

            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel = item["snippet"]["channelTitle"]

            candidates.append(
                {
                    "video_id": video_id,
                    "title": title,
                    "channel": channel,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )

    return candidates