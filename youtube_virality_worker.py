# youtube_virality_worker.py
"""
Leninware Virality Worker
Scores videos and sends winners to the Leninware pipeline.
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

VIRALITY_THRESHOLD = 2.0
MAX_VIDEOS_PER_RUN = 2


def compute_virality_score(v: Dict[str, Any]) -> float:
    views = v.get("view_count", 0)
    likes = v.get("like_count", 0)
    comments = v.get("comment_count", 0)

    pub = v.get("published_at")
    now = dt.datetime.now(dt.timezone.utc)
    age_hours = max((now - pub).total_seconds() / 3600, 1)

    engagement = likes * 2 + comments * 3
    velocity = (views + engagement * 10) / age_hours

    score = 0.4 * math.log10(max(views, 1)) + 0.6 * math.log10(velocity + 1)
    return round(score, 2)


def run_virality_pass():
    print("=== Leninware Virality Worker ===")

    videos = get_candidate_videos(max_per_feed=10)
    if not videos:
        print("No videos found.")
        return

    # Score everything
    for v in videos:
        v["virality_score"] = compute_virality_score(v)

    # Log sorted scores
    for v in sorted(videos, key=lambda x: x["virality_score"], reverse=True):
        print(
            f"\nTitle:   {v['title']}\n"
            f"Channel: {v['channel']}\n"
            f"URL:     {v['url']}\n"
            f"Views:   {v['view_count']}\n"
            f"Likes:   {v['like_count']}\n"
            f"Comments:{v['comment_count']}\n"
            f"Score:   {v['virality_score']}"
        )

    winners = [v for v in videos if v["virality_score"] >= VIRALITY_THRESHOLD]
    winners.sort(key=lambda x: x["virality_score"], reverse=True)
    winners = winners[:MAX_VIDEOS_PER_RUN]

    if not winners:
        print("\nNo videos crossed the threshold.")
        return

    print(f"\nProcessing {len(winners)} winners...")

    for v in winners:
        print(f"\n=== Working on: {v['title']} ===")

        # Step 1: Generate commentary
        script = generate_leninware_tts_from_url(v["url"])

        # Step 2: Render (stub)
        rendered = render_video_with_shotstack(script, v["title"])

        # Step 3: Upload (stub)
        if rendered:
            upload_to_youtube_stub(
                path_or_url=rendered,
                title=v["title"],
                description=f"Auto-generated Leninware response to {v['url']}",
            )

    print("\n=== Virality Pass Complete ===")


if __name__ == "__main__":
    run_virality_pass()