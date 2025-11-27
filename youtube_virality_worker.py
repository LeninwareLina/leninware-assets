# youtube_virality_worker.py

import os
import logging
import re
from typing import Dict, List, Any
import requests
from youtube_ingest import get_recent_candidates   # IMPORTANT: matches your old pipeline

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# Hard caps to protect quota
MAX_CANDIDATES_PER_RUN = 20
VIRALITY_THRESHOLD = 6.0


def _extract_video_id(url: str) -> str:
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", url):
        return url

    m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
    if m:
        return m.group(1)

    m = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
    if m:
        return m.group(1)

    return url


def _fetch_stats(video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY not set")
        return {}

    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY,
    }

    try:
        resp = requests.get(
            f"{YOUTUBE_API_BASE}/videos",
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
    except Exception as e:
        logger.error("YouTube stats fetch error: %s", e)
        return {}

    data = resp.json()
    out = {}

    for item in data.get("items", []):
        vid = item.get("id")
        if vid:
            out[vid] = item.get("statistics", {})

    return out


def _score(candidate: Dict[str, Any], stats: Dict[str, Any]) -> float:
    try:
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
    except:
        views = likes = comments = 0

    base = float(candidate.get("score", 0))
    like_ratio = likes / views if views > 0 else 0
    comment_ratio = comments / views if views > 0 else 0

    return base + (like_ratio * 10) + (comment_ratio * 20)


def run_virality_pass() -> List[Dict[str, Any]]:
    """
    IMPORTANT:
    main.py calls run_virality_pass() with NO arguments.
    So we must obtain the candidates internally (like your original pipeline).
    """

    candidates = get_recent_candidates()

    if not candidates:
        logger.info("[virality] No candidates returned by ingester")
        return []

    # Limit candidates to keep quota safe
    candidates = sorted(
        candidates,
        key=lambda c: c.get("score", 0),
        reverse=True,
    )[:MAX_CANDIDATES_PER_RUN]

    video_ids = []
    for c in candidates:
        vid = _extract_video_id(c.get("url", ""))
        c["video_id"] = vid
        video_ids.append(vid)

    stats = _fetch_stats(video_ids)

    scored = []
    for c in candidates:
        vid = c["video_id"]
        if vid not in stats:
            continue

        viral_score = _score(c, stats[vid])
        c["virality_score"] = viral_score
        c["statistics"] = stats[vid]

        if viral_score >= VIRALITY_THRESHOLD:
            scored.append(c)

    scored.sort(key=lambda c: c["virality_score"], reverse=True)

    logger.info(
        "[virality] %d candidates in → %d passed threshold %.2f",
        len(candidates),
        len(scored),
        VIRALITY_THRESHOLD,
    )

    return scored