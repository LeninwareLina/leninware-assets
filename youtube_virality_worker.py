# youtube_virality_worker.py

import requests
from typing import List, Dict
from config import USE_MOCK_AI, YOUTUBE_API_KEY


def _get_stats(video_id: str):
    """
    Fetch YouTube stats for a video.
    MOCK MODE: Return fake stats.
    """

    # ----------------------------------------------------
    # MOCK MODE — return stable fake stats
    # ----------------------------------------------------
    if USE_MOCK_AI:
        # Deterministic fake stats based on video_id hash
        base = abs(hash(video_id)) % 5000
        return {
            "views": 5000 + base,
            "likes": 100 + (base % 300),
        }

    # ----------------------------------------------------
    # REAL MODE — call YouTube API
    # ----------------------------------------------------
    url = (
        "https://www.googleapis.com/youtube/v3/videos"
        f"?key={YOUTUBE_API_KEY}"
        f"&part=statistics"
        f"&id={video_id}"
    )

    resp = requests.get(url).json()
    items = resp.get("items", [])
    if not items:
        return None

    stats = items[0].get("statistics", {})
    return {
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)) if "likeCount" in stats else 0,
    }


def run_virality_pass(candidates: List[Dict]) -> List[Dict]:
    """
    Calculate a virality score and sort the candidates.
    """
    scored = []

    for c in candidates:
        stats = _get_stats(c["video_id"])
        if not stats:
            continue

        views = stats["views"]
        likes = stats["likes"]

        # Simple virality formula
        score = views + (likes * 20)

        scored.append({
            **c,
            "views": views,
            "likes": likes,
            "virality": score,
        })

    scored.sort(key=lambda x: x["virality"], reverse=True)
    return scored