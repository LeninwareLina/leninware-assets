# youtube_virality_worker.py

import math
import datetime as dt
from typing import List, Dict, Any

from youtube_ingest import get_candidate_videos
from transcript_fetcher import fetch_transcript
from leninware_commentary import generate_leninware_commentary
from image_prompt_builder import build_image_prompts_from_commentary
from image_generator import generate_images
from shotstack_renderer import render_video_with_shotstack


VIRALITY_THRESHOLD = 2.0
MAX_VIDEOS_PER_RUN = 2


def compute_virality_score(video: Dict[str, Any]) -> float:
    views = int(video.get("view_count") or 0)
    likes = int(video.get("like_count") or 0)
    comments = int(video.get("comment_count") or 0)

    published_at = video.get("published_at")
    if isinstance(published_at, dt.datetime):
        now = dt.datetime.now(dt.timezone.utc)
        age_hours = max((now - published_at).total_seconds() / 3600.0, 1.0)
    else:
        age_hours = 24.0

    engagement = likes * 2 + comments * 3
    velocity = (views + engagement * 10) / age_hours

    score = 0.4 * math.log10(max(views, 1)) + 0.6 * math.log10(velocity + 1.0)
    return round(score, 2)


def run_virality_pass() -> None:
    print("=== Leninware YouTube Virality Worker ===")

    videos: List[Dict[str, Any]] = get_candidate_videos(max_per_feed=5)
    if not videos:
        print("No videos fetched from feeds.")
        return

    for v in videos:
        v["virality_score"] = compute_virality_score(v)

    # Log scored videos
    for v in sorted(videos, key=lambda x: x["virality_score"], reverse=True):
        print(
            f"Title: {v['title']}\n"
            f"Channel: {v['channel']}\n"
            f"URL: {v['url']}\n"
            f"Views: {v['view_count']} | Likes: {v['like_count']} | Comments: {v['comment_count']}\n"
            f"Score: {v['virality_score']}\n"
        )

    winners = [v for v in videos if v["virality_score"] >= VIRALITY_THRESHOLD]
    winners.sort(key=lambda x: x["virality_score"], reverse=True)
    winners = winners[:MAX_VIDEOS_PER_RUN]

    if not winners:
        print(f"No videos crossed virality threshold ({VIRALITY_THRESHOLD}). Nothing to process.")
        return

    print(f"{len(winners)} videos crossed threshold; sending to Leninware pipeline.")

    for v in winners:
        print("\n=== Processing candidate ===")
        print(f"Channel: {v['channel']}")
        print(f"Title:   {v['title']}")
        print(f"URL:     {v['url']}")
        print(f"Score:   {v['virality_score']}")

        # Transcript
        try:
            transcript = fetch_transcript(v["url"])
        except Exception as e:
            print(f"[worker] Transcript failed: {e}")
            continue

        # Commentary
        try:
            commentary = generate_leninware_commentary(transcript)
        except Exception as e:
            print(f"[worker] Leninware commentary failed: {e}")
            continue

        print("\n--- Leninware Commentary ---")
        print(commentary[:600], "...\n")

        # Image prompts
        prompts = build_image_prompts_from_commentary(commentary)
        print("[worker] Image prompts:")
        for p in prompts:
            print("  -", p)

        # Generate images
        try:
            image_paths = generate_images(prompts)
        except Exception as e:
            print(f"[worker] Image generation failed: {e}")
            image_paths = []

        # Render video stub
        render_video_with_shotstack(
            audio_path=None,  # hook in TTS later if you want
            image_paths=image_paths,
            title=v["title"],
        )

    print("\n=== Virality pass complete. ===")