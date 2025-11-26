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


def score_video(video: Dict[str, Any]) -> float:
    """
    Simple virality scoring. Higher = more viral.
    """
    views = video.get("views", 0) or 0
    likes = video.get("likes", 0) or 0
    comments = video.get("comments", 0) or 0

    if views == 0:
        return 0.0

    engagement = (likes + comments) / max(views, 1)
    return round(engagement * 100, 2)


def run_virality_pass():
    print("=== Running virality pass ===")

    candidates = get_candidate_videos()
    print(f"Found {len(candidates)} candidates")

    scored = []
    for v in candidates:
        s = score_video(v)
        v["score"] = s
        print(f"  {v['title']}: score={s}")
        if s >= VIRALITY_THRESHOLD:
            scored.append(v)

    # Limit the number processed per pass
    scored = scored[:MAX_VIDEOS_PER_RUN]

    if not scored:
        print("No videos crossed threshold.")
        return

    print(f"{len(scored)} videos crossed threshold; processing...")

    for v in scored:
        print(f"\n=== Processing candidate ===")
        print(f"Channel: {v['channel']}")
        print(f"Title: {v['title']}")
        print(f"URL: {v['url']}")
        print(f"Score: {v['score']}")

        # Fetch transcript
        try:
            transcript = fetch_transcript(v["url"])
            print(f"[worker] Transcript length: {len(transcript)}")
        except Exception as e:
            print(f"[worker] Transcript fetch failed: {e}")
            continue

        # Generate commentary
        try:
            commentary = generate_leninware_commentary(transcript)
        except Exception as e:
            print(f"[worker] Commentary generation failed: {e}")
            continue

        print("\n--- Leninware Commentary ---")
        print(commentary)

        # Build image prompts
        prompts = build_image_prompts_from_commentary(commentary)

        # Generate images
        try:
            image_paths = generate_images(prompts)
        except Exception as e:
            print(f"[worker] Image generation failed: {e}")
            image_paths = []

        # Render video (stub)
        render_video_with_shotstack(
            audio_path=None,
            image_paths=image_paths,
            title=v["title"],
        )

    print("\n=== Virality pass complete. ===")