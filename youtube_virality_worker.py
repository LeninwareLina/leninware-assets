import os
import sys
import json
import math
import datetime
import requests

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEOS_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"

# Default threshold for "good enough to process"
DEFAULT_THRESHOLD = 6.0


def _parse_published_at(published_at_str: str) -> datetime.datetime:
    """
    Parse an ISO 8601 publishedAt string into a UTC datetime.
    """
    # Examples: "2025-11-27T14:23:10Z"
    if not published_at_str:
        return datetime.datetime.utcnow()

    try:
        if published_at_str.endswith("Z"):
            published_at_str = published_at_str[:-1]
        return datetime.datetime.fromisoformat(published_at_str)
    except Exception:
        return datetime.datetime.utcnow()


def compute_score(snippet: dict, statistics: dict) -> float:
    """
    Compute a simple 0–10 virality score based on:
      - total views
      - view velocity (views per hour since publish)
      - like ratio
      - comment activity
      - recency penalty
    """

    now = datetime.datetime.utcnow()
    published_at_str = snippet.get("publishedAt") or ""
    published_dt = _parse_published_at(published_at_str)
    hours_since = max((now - published_dt).total_seconds() / 3600.0, 1.0)

    views = int(statistics.get("viewCount", "0") or 0)
    likes = int(statistics.get("likeCount", "0") or 0)
    comments = int(statistics.get("commentCount", "0") or 0)

    # Basic components
    view_velocity = views / hours_since  # views per hour
    like_ratio = (likes / views) if views > 0 else 0.0
    comment_rate = comments / hours_since  # comments per hour

    # Log-scale for views & velocity (avoid huge blowups)
    views_term = math.log10(views + 1) * 2.0          # up to ~10 for viral content
    velocity_term = math.log10(view_velocity + 1) * 2.0

    # Engagement factors
    like_term = like_ratio * 3.0                      # 0–3
    comment_term = min(comment_rate / 5.0, 2.0)       # cap at +2

    # Slight penalty for older videos
    recency_penalty = min(hours_since / 48.0, 3.0)    # max -3 after ~4 days

    raw_score = views_term + velocity_term + like_term + comment_term - recency_penalty

    # Clamp to [0, 10]
    score = max(0.0, min(10.0, raw_score))
    return round(score, 2)


def fetch_stats_for_candidates(candidates: list[dict]) -> dict:
    """
    Given a list of candidates with 'video_id',
    fetch snippet+statistics for all in a single videos.list call.

    Returns a dict: {video_id: (snippet, statistics)}.
    """
    if not YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is not set")

    video_ids = [c["video_id"] for c in candidates if "video_id" in c]
    # Deduplicate
    video_ids = list(dict.fromkeys(video_ids))

    if not video_ids:
        return {}

    # YouTube lets up to 50 IDs per call
    ids_param = ",".join(video_ids[:50])

    params = {
        "part": "snippet,statistics",
        "id": ids_param,
        "key": YOUTUBE_API_KEY,
    }

    resp = requests.get(VIDEOS_ENDPOINT, params=params, timeout=20)
    data = resp.json()

    if "error" in data:
        reason = data["error"]["errors"][0].get("reason", "unknown")
        message = data["error"].get("message", "")
        print(f"[virality] YouTube API error: {reason} - {message}", file=sys.stderr)
        return {}

    results = {}
    for item in data.get("items", []):
        vid = item.get("id")
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        if vid:
            results[vid] = (snippet, statistics)

    return results


def score_candidates(candidates: list[dict], threshold: float = DEFAULT_THRESHOLD) -> list[dict]:
    """
    Take a list of candidates (each with 'video_id'),
    fetch stats once, compute scores, and return only those
    that meet or exceed the threshold.
    """
    stats_map = fetch_stats_for_candidates(candidates)
    scored = []

    for c in candidates:
        vid = c.get("video_id")
        if not vid or vid not in stats_map:
            continue

        snippet, statistics = stats_map[vid]
        score = compute_score(snippet, statistics)
        c = dict(c)  # shallow copy
        c["score"] = score
        scored.append(c)

    # Filter by threshold
    filtered = [c for c in scored if c.get("score", 0) >= threshold]

    # Sort descending by score
    filtered.sort(key=lambda x: x.get("score", 0), reverse=True)
    return filtered


def main():
    """
    CLI entrypoint:
    - Read JSON list of candidates from stdin
    - Add scores
    - Filter by DEFAULT_THRESHOLD
    - Print JSON list to stdout
    """
    raw = sys.stdin.read().strip()
    if not raw:
        print("[]")
        return

    try:
        candidates = json.loads(raw)
    except json.JSONDecodeError:
        print("[]")
        return

    if not isinstance(candidates, list):
        print("[]")
        return

    filtered = score_candidates(candidates, threshold=DEFAULT_THRESHOLD)
    print(json.dumps(filtered))


if __name__ == "__main__":
    main()