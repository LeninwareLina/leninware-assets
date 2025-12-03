import re
from pathlib import Path
from typing import List, Dict
import requests
import isodate

from config import USE_MOCK_AI, YOUTUBE_API_KEY

CHANNELS_FILE = Path("prompts/youtube_channels.txt")
CHANNEL_URL_RE = re.compile(r"/channel/([A-Za-z0-9_-]+)")


def load_channel_ids() -> List[str]:
    if not CHANNELS_FILE.exists():
        raise FileNotFoundError(f"Missing channel list: {CHANNELS_FILE}")

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

    print(f"[ingest] Loaded {len(ids)} channels from {CHANNELS_FILE}")
    return ids


def _get_video_duration(video_id: str) -> int:
    """
    Returns video duration in seconds.
    Returns 0 for Shorts or unknown.
    """

    print(f"[ingest] Fetching duration for video: {video_id}")

    url = (
        "https://www.googleapis.com/youtube/v3/videos"
        f"?key={YOUTUBE_API_KEY}"
        "&part=contentDetails"
        f"&id={video_id}"
    )

    try:
        resp = requests.get(url).json()
    except Exception as e:
        print(f"[ingest] ERROR requesting duration for {video_id}: {e}")
        return 0

    items = resp.get("items", [])
    if not items:
        print(f"[ingest] No duration info for {video_id} (items empty)")
        return 0

    iso = items[0]["contentDetails"].get("duration")
    if not iso:
        print(f"[ingest] Missing ISO duration for {video_id}")
        return 0

    try:
        duration = int(isodate.parse_duration(iso).total_seconds())
        print(f"[ingest] Duration for {video_id}: {duration}s")
        return duration
    except Exception as e:
        print(f"[ingest] Failed to parse duration '{iso}' for {video_id}: {e}")
        return 0


def get_recent_candidates(max_results: int = 5) -> List[Dict]:
    """
    Returns list of video candidates.
    MOCK MODE: Generates fake long-form videos to avoid API cost.
    """

    # ----------------------------------------------------
    # MOCK MODE
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print("[ingest:mock] Returning mock YouTube videos.")
        mock = [
            {
                "video_id": f"mockvideo{i}",
                "title": f"Mock Video #{i}",
                "channel": "Mock Channel",
                "duration_s": 300 + i * 10,
                "url": f"https://www.youtube.com/watch?v=mockvideo{i}",
            }
            for i in range(1, max_results + 1)
        ]
        print(f"[ingest:mock] Produced {len(mock)} mock videos")
        return mock

    # ----------------------------------------------------
    # REAL MODE — Call YouTube API
    # ----------------------------------------------------
    channel_ids = load_channel_ids()
    candidates = []

    print(f"[ingest] Starting ingest across {len(channel_ids)} channels...")

    for channel_id in channel_ids:
        print(f"\n[ingest] Querying channel: {channel_id}")

        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?key={YOUTUBE_API_KEY}"
            f"&channelId={channel_id}"
            "&part=snippet"
            "&order=date"
            f"&maxResults={max_results}"
        )

        try:
            resp = requests.get(url).json()
        except Exception as e:
            print(f"[ingest] ERROR calling YouTube search for {channel_id}: {e}")
            continue

        items = resp.get("items", [])
        print(f"[ingest] API returned {len(items)} items")

        if "error" in resp:
            print(f"[ingest] YT API ERROR: {resp['error']}")
            continue

        for item in items:
            kind = item.get("id", {}).get("kind")
            if kind != "youtube#video":
                print(f"[ingest] Skipping non-video item: {kind}")
                continue

            video_id = item["id"].get("videoId")
            title = item["snippet"]["title"]
            channel_title = item["snippet"]["channelTitle"]
            watch_url = f"https://www.youtube.com/watch?v={video_id}"

            print(f"\n[ingest] Found video:")
            print(f"         Title: {title}")
            print(f"         ID:    {video_id}")

            # ------------------------------------------------
            # Fetch duration
            # ------------------------------------------------
            dur_s = _get_video_duration(video_id)

            if dur_s <= 0:
                print(f"[ingest] Rejecting '{title}' — could not determine duration")
                continue

            if dur_s < 300:
                print(f"[ingest] Rejecting '{title}' — too short ({dur_s}s)")
                continue

            print(f"[ingest] ACCEPTING '{title}' ({dur_s}s)")

            candidates.append(
                {
                    "video_id": video_id,
                    "title": title,
                    "channel": channel_title,
                    "duration_s": dur_s,
                    "url": watch_url,
                }
            )

    print(f"\n[ingest] Finished ingest. Accepted {len(candidates)} videos total.")
    return candidates