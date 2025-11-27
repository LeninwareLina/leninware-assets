# youtube_virality_worker.py

import os
import logging
import re
from typing import Dict, List, Any

import requests

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# Hard caps so we don't blast the quota
MAX_CANDIDATES_PER_RUN = int(os.environ.get("MAX_VIRALITY_CANDIDATES", "20"))
DEFAULT_VIRALITY_THRESHOLD = float(os.environ.get("VIRALITY_THRESHOLD", "6.0"))


def _extract_video_id(url: str) -> str:
    """
    Try to extract a YouTube video ID from a URL or ID string.
    """
    # If it's already an 11-char ID, just use it
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", url):
        return url

    # Standard watch URL
    m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
    if m:
        return m.group(1)

    # Short youtu.be URL
    m = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
    if m:
        return m.group(1)

    return url  # fall back; worst-case API will complain


def _fetch_stats(video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetch basic statistics for a batch of video IDs.
    Returns a mapping video_id -> stats dict.
    """
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY not set in environment")
        return {}

    stats_by_id: Dict[str, Dict[str, Any]] = {}

    # YouTube videos.list supports up to 50 IDs per call; we’ll be well under that.
    ids_param = ",".join(video_ids)
    params = {
        "part": "statistics",
        "id": ids_param,
        "key": YOUTUBE_API_KEY,
    }

    try:
        resp = requests.get(
            f"{YOUTUBE_API_BASE}/videos",
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("Error calling YouTube videos.list: %s", e)
        return {}

    data = resp.json()
    for item in data.get("items", []):
        vid = item.get("id")
        stats = item.get("statistics", {})
        if vid:
            stats_by_id[vid] = stats

    return stats_by_id


def _compute_virality_score(candidate: Dict[str, Any], stats: Dict[str, Any]) -> float:
    """
    Heuristic virality score based on YouTube statistics.
    You can tune this, but keep the function name stable.
    """
    try:
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
    except ValueError:
        views = likes = comments = 0

    # Avoid division by zero
    like_ratio = likes / views if views > 0 else 0.0
    comment_ratio = comments / views if views > 0 else 0.0

    # Use the ingester's heuristic score as a base if present
    base_score = float(candidate.get("score", 0.0))

    # Very simple combined metric; tune later if needed.
    virality = base_score + (like_ratio * 10.0) + (comment_ratio * 20.0)

    return virality


def run_virality_pass(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Main entrypoint expected by main.py.

    - Takes a list of candidate dicts (from the ingester)
    - Fetches YouTube stats for the top N by initial score
    - Computes a virality score
    - Returns only candidates whose virality_score >= threshold,
      sorted descending by virality_score.
    """
    if not candidates:
        logger.info("[virality] No candidates provided")
        return []

    # Sort by initial ingester score (if present), then cut to a safe max
    sorted_candidates = sorted(
        candidates,
        key=lambda c: c.get("score", 0),
        reverse=True,
    )[:MAX_CANDIDATES_PER_RUN]

    video_ids = []
    for c in sorted_candidates:
        vid = c.get("video_id") or _extract_video_id(c.get("url", ""))
        c["video_id"] = vid
        video_ids.append(vid)

    stats_by_id = _fetch_stats(video_ids)
    if not stats_by_id:
        logger.warning("[virality] No stats fetched; returning empty list")
        return []

    scored: List[Dict[str, Any]] = []
    for c in sorted_candidates:
        vid = c["video_id"]
        stats = stats_by_id.get(vid)
        if not stats:
            continue
        virality_score = _compute_virality_score(c, stats)
        enriched = {
            **c,
            "virality_score": virality_score,
            "statistics": stats,
        }
        scored.append(enriched)

    # Filter & sort by virality_score
    threshold = DEFAULT_VIRALITY_THRESHOLD
    viral = [c for c in scored if c["virality_score"] >= threshold]
    viral.sort(key=lambda c: c["virality_score"], reverse=True)

    logger.info(
        "[virality] %d candidates in, %d above threshold %.2f",
        len(candidates),
        len(viral),
        threshold,
    )

    return viral