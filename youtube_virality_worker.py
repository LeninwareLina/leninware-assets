# youtube_virality_worker.py

import os
import logging
import math
import requests
from typing import List, Dict, Any
from youtube_ingest import get_recent_candidates

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3/videos"

# Tunables
MAX_CANDIDATES_PER_RUN = 30
VIRALITY_THRESHOLD = 5.5       # Lowered so we get real output
MAX_FINAL_RESULTS = 3          # Don’t overwhelm your pipeline


def fetch_stats(video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetch statistics for a batch of video IDs in ONE API call.
    """
    if not YOUTUBE_API_KEY:
        logger.error("Missing YOUTUBE_API_KEY")
        return {}

    params = {
        "key": YOUTUBE_API_KEY,
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
    }

    try:
        resp = requests.get(YOUTUBE_API_BASE, params=params, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"YouTube stats error: {e}")
        return {}

    data = resp.json()
    out = {}

    for item in data.get("items", []):
        vid = item.get("id")
        if vid:
            out[vid] = {
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "comments": int(item["statistics"].get("commentCount", 0)),
                "published_at": item["snippet"].get("publishedAt"),
            }

    return out


def score_candidate(c: Dict[str, Any], stats: Dict[str, Any]) -> float:
    """
    Simple, effective, engagement-driven virality score: 0–10
    """
    views = stats["views"]
    likes = stats["likes"]
    comments = stats["comments"]

    like_ratio = (likes / views) if views > 0 else 0
    comment_ratio = (comments / views) if views > 0 else 0

    # Log scaling keeps things sane
    views_term = math.log10(views + 1) * 2.2
    velocity_term = math.log10((likes + comments + 1)) * 1.6

    engagement = (like_ratio * 4.5) + (comment_ratio * 7)

    total = views_term + velocity_term + engagement
    total = max(0, min(10, total))

    return round(total, 2)


def run_virality_pass() -> List[Dict[str, Any]]:
    """
    MAIN ENTRY POINT (called by main.py)
    No arguments allowed — must pull candidates internally.
    """
    candidates = get_recent_candidates()

    if not candidates:
        logger.info("[virality] No candidates found.")
        return []

    # Limit the number we score
    candidates = candidates[:MAX_CANDIDATES_PER_RUN]

    video_ids = [c["video_id"] for c in candidates]
    stats_map = fetch_stats(video_ids)

    scored = []
    for c in candidates:
        vid = c["video_id"]
        stats = stats_map.get(vid)
        if not stats:
            continue

        vscore = score_candidate(c, stats)
        c["virality_score"] = vscore
        c["statistics"] = stats

        if vscore >= VIRALITY_THRESHOLD:
            scored.append(c)

    # Sort by highest virality
    scored.sort(key=lambda x: x["virality_score"], reverse=True)

    # Only pass best few to avoid overloading the pipeline
    final = scored[:MAX_FINAL_RESULTS]

    logger.info(
        "[virality] %d candidates in → %d passed threshold → %d forwarded",
        len(candidates),
        len(scored),
        len(final),
    )

    return final