# youtube_virality_worker.py

import logging
import math
from typing import List, Dict, Any

import requests

from youtube_ingest import get_recent_candidates
from config import require_env

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = require_env("YOUTUBE_API_KEY")
VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"

# Tunables
MAX_CANDIDATES_PER_RUN = 30     # Max from ingest we will score
VIRALITY_THRESHOLD = 5.5        # 0–10; lower to allow more through
MAX_FINAL_RESULTS = 3           # Number of top videos to forward


def _fetch_stats(video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch views/likes/comments for a batch of video IDs in ONE API call."""
    if not video_ids:
        return {}

    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY,
    }

    try:
        resp = requests.get(VIDEOS_API_URL, params=params, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"[virality] YouTube stats error: {e}")
        return {}

    data = resp.json()
    out: Dict[str, Dict[str, Any]] = {}

    for item in data.get("items", []):
        vid = item.get("id")
        stats = item.get("statistics", {}) or {}
        if not vid:
            continue
        try:
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
        except Exception:
            views = likes = comments = 0

        out[vid] = {
            "views": views,
            "likes": likes,
            "comments": comments,
        }

    return out


def _score_candidate(stats: Dict[str, Any]) -> float:
    """Compute a simple 0–10 virality score from basic stats."""
    views = stats["views"]
    likes = stats["likes"]
    comments = stats["comments"]

    like_ratio = (likes / views) if views > 0 else 0.0
    comment_ratio = (comments / views) if views > 0 else 0.0

    # Log scaling for stability
    views_term = math.log10(views + 1) * 2.2
    engagement_term = math.log10(likes + comments + 1) * 1.8
    social_term = like_ratio * 4.5 + comment_ratio * 7.0

    score = views_term + engagement_term + social_term
    score = max(0.0, min(10.0, score))
    return round(score, 2)


def run_virality_pass() -> List[Dict[str, Any]]:
    """Main entrypoint called by main.py.

    - Fetches recent candidates from ingest
    - Fetches stats for each
    - Computes virality scores
    - Returns a small list of top candidates
    """
    candidates = get_recent_candidates()

    if not candidates:
        logger.info("[virality] No candidates from ingest.")
        return []

    # Trim to a safe number before stats fetch
    candidates = candidates[:MAX_CANDIDATES_PER_RUN]

    video_ids = [c["video_id"] for c in candidates]
    stats_map = _fetch_stats(video_ids)

    scored: List[Dict[str, Any]] = []

    for c in candidates:
        vid = c["video_id"]
        stats = stats_map.get(vid)
        if not stats:
            continue

        vscore = _score_candidate(stats)
        enriched = dict(c)
        enriched["virality_score"] = vscore
        enriched["statistics"] = stats
        scored.append(enriched)

    # Filter by threshold
    passed = [c for c in scored if c["virality_score"] >= VIRALITY_THRESHOLD]

    # Sort descending
    passed.sort(key=lambda x: x["virality_score"], reverse=True)

    final = passed[:MAX_FINAL_RESULTS]

    logger.info(
        "[virality] %d candidates scored, %d passed threshold %.2f, %d forwarded",
        len(candidates),
        len(passed),
        VIRALITY_THRESHOLD,
        len(final),
    )

    return final