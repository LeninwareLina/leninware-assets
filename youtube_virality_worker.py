# youtube_virality_worker.py
"""
Leninware YouTube Virality Worker

Flow:
1. Fetch recent videos from configured RSS feeds.
2. Enrich with basic stats (views, likes, comments) via YouTube Data API.
3. Compute a simple virality score using engagement + recency.
4. Log all scores.
5. For top-scoring videos:
      - generate a Leninware TTS script via Claude Sonnet-4,
      - (optionally) send to Shotstack,
      - (optionally) upload result to YouTube.

Shotstack + upload are currently stubs in leninware_video_pipeline.py.
"""

import math
import datetime as dt
from typing import List, Dict, Any

from youtube_ingest import get_candidate_videos
from leninware_video_pipeline import (
    generate_leninware_tts_from_url,
    render_video_with_shotstack,
    upload_to_youtube_stub,
)

# How “picky” the worker is
VIRALITY_THRESHOLD = 2.0   # lower => more videos get picked
MAX_VIDEOS_PER_RUN = 2     # don’t melt your API quota


# === Scoring ================================================================

def compute_virality_score(video: Dict[str, Any]) -> float:
    """
    Heuristic, fully deterministic virality score.

    Inputs:
        - view_count
        - like_count
        - comment_count
        - age (in hours)

    Intuition:
        - more views = good
        - more likes/comments = better
        - newer video with same stats = much better
    """
    views = int(video.get("view_count") or 0)
    likes = int(video.get("like_count") or 0)
    comments = int(video.get("comment_count") or 0)

    published_at = video.get("published_at")
    if isinstance(published_at, dt.datetime):
        now = dt.datetime.now(dt.timezone.utc)
        age_hours = max((now - published_at).total_seconds() / 3600.0, 1.0)
    else:
        age_hours = 24.0  # shrug

    engagement = likes * 2 + comments * 3
    velocity = (views + engagement * 10) / age_hours

    # log-scaled views + log-scaled velocity
    score = 0.4 * math.log10(max(views, 1)) + 0.6 * math.log10(velocity + 1.0)
    return round(score, 2)


# === Worker ================================================================

def run_virality_pass() -> None:
    print("=== Leninware YouTube Virality Worker ===")

    videos: List[Dict[str, Any]] = get_candidate_videos(max_per_feed=10)
    if not videos:
        print("No videos fetched from feeds.")
        return

    # Score all videos
    for v in videos:
        v["virality_score"] = compute_virality_score(v)

    # Log them for you to inspect
    for v in sorted(videos, key=lambda x: x["virality_score"], reverse=True):
        title = v["title"]
        chan = v["channel"]
        url = v["url"]
        vs = v.get("view_count", 0)
        ls = v.get("like_count", 0)
        cs = v.get("comment_count", 0)
        score = v["virality_score"]
        print(
            f"Title: {title}\n"
            f"Channel: {chan}\n"
            f"URL: {url}\n"
            f"Views: {vs} | Likes: {ls} | Comments: {cs}\n"
            f"Score: {score}\n"
        )

    # Pick winners
    winners = [
        v
        for v in videos
        if v["virality_score"] >= VIRALITY_THRESHOLD
    ]
    winners.sort(key=lambda x: x["virality_score"], reverse=True)
    winners = winners[:MAX_VIDEOS_PER_RUN]

    if not winners:
        print(f"No videos crossed virality threshold ({VIRALITY_THRESHOLD}). "
              f"Nothing sent to Leninware pipeline.")
        return

    print(f"{len(winners)} videos crossed threshold; sending to Leninware pipeline.")

    for v in winners:
        print("\n=== Processing candidate ===")
        print(f"Channel: {v['channel']}")
        print(f"Title:   {v['title']}")
        print(f"URL:     {v['url']}")
        print(f"Score:   {v['virality_score']}")

        # Step 1: generate Leninware TTS script
        tts_script = generate_leninware_tts_from_url(v["url"])

        # Step 2: render video via Shotstack (stub for now)
        rendered_url_or_path = render_video_with_shotstack(tts_script, v["title"])

        # Step 3: upload to YouTube (stub for now)
        if rendered_url_or_path:
            upload_to_youtube_stub(
                rendered_video_path_or_url=rendered_url_or_path,
                title=v["title"],
                description=f"Auto-generated Leninware response to: {v['url']}",
            )

    print("\n=== Virality pass complete. ===")


if __name__ == "__main__":
    run_virality_pass()