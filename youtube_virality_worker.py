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
        base = abs(hash(video_id)) % 5000
        print(f"[virality:mock] Stats for {video_id}: views={5000+base}, likes={100+(base%300)}")
        return {
            "views": 5000 + base,
            "likes": 100 + (base % 300),
        }

    # ----------------------------------------------------
    # REAL MODE — call YouTube API
    # ----------------------------------------------------
    print(f"[virality] Fetching stats for video: {video_id}")

    url = (
        "https://www.googleapis.com/youtube/v3/videos"
        f"?key={YOUTUBE_API_KEY}"
        f"&part=statistics"
        f"&id={video_id}"
    )

    try:
        resp = requests.get(url).json()
    except Exception as e:
        print(f"[virality] ERROR requesting stats for {video_id}: {e}")
        return None

    if "error" in resp:
        print(f"[virality] API ERROR for {video_id}: {resp['error']}")
        return None

    items = resp.get("items", [])
    if not items:
        print(f"[virality] No stats available for {video_id} (items empty)")
        return None

    stats = items[0].get("statistics", {})
    if not stats:
        print(f"[virality] Stats missing for {video_id}")
        return None

    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0)) if "likeCount" in stats else 0

    print(f"[virality] Stats for {video_id}: views={views}, likes={likes}")

    return {
        "views": views,
        "likes": likes,
    }


def run_virality_pass(candidates: List[Dict]) -> List[Dict]:
    """
    Calculate a virality score and sort the candidates.
    """

    print(f"[virality] Starting virality scoring for {len(candidates)} candidates")

    scored = []

    for c in candidates:
        print(f"\n[virality] Processing candidate: {c['title']} ({c['video_id']})")

        stats = _get_stats(c["video_id"])
        if not stats:
            print(f"[virality] Skipping {c['video_id']} — no stats available")
            continue

        views = stats["views"]
        likes = stats["likes"]
        score = views + (likes * 20)

        print(f"[virality] Computed score: {score}  (views={views}, likes={likes})")

        scored.append({
            **c,
            "views": views,
            "likes": likes,
            "virality": score,
        })

    print(f"\n[virality] Sorting {len(scored)} scored candidates...")
    scored.sort(key=lambda x: x["virality"], reverse=True)

    print("[virality] Final ranking:")
    for s in scored:
        print(f"  {s['title']} — score={s['virality']} (views={s['views']}, likes={s['likes']})")

    return scored