import requests
from config import YOUTUBE_API_KEY

# Channels Leninware originally pulled from.
# These were in the old repo.
CHANNELS = [
    "UCXIJgqnII2ZOINSWNOGFThA",  # Fox News
    "UC7yRILFFJ2zI_Ut9oZuDbWw",  # TYT
    "UC6TmAlx4q_GU8Z1LENzOdJw",  # Some news outlets
    "UCaXkIU1QidjPwiAYu6GcHjg",  # MeidasTouch
    "UCq16dvHk1FWk0TDvFu4CFOw",  # Brian Tyler Cohen
    "UCZJb0pVQF8l0Zo4QCXFvSrg",  # Beau of the Fifth Column
    "UCSPIZo7bGZpL8T3cHrIu9Kw",  # LegalEagle
]

API_URL = "https://www.googleapis.com/youtube/v3/search"


def fetch_channel_videos(channel_id: str):
    """Return a list of raw video items from a YouTube channel."""
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 20,
        "type": "video",
    }

    resp = requests.get(API_URL, params=params, timeout=20)

    if resp.status_code != 200:
        raise RuntimeError(f"YoutubeAPI 403/400: {resp.text}")

    return resp.json().get("items", [])


def get_candidate_videos() -> list:
    """Fetch videos from all configured channels and flatten list."""
    all_items = []

    for cid in CHANNELS:
        try:
            items = fetch_channel_videos(cid)
            all_items.extend(items)
        except Exception as e:
            print(f"[ingest] Failed to fetch for {cid}: {e}")

    return all_items