# youtube_virality_worker.py
import time
import traceback

from youtube_ingest import get_candidate_videos
from leninware_video_pipeline import generate_leninware_tts_from_url


# === CONFIG ===
VIRALITY_THRESHOLD = 2.2        # Score required for processing
MAX_VIDEOS_TO_PROCESS = 3       # Hard limit per pass to prevent overload
SLEEP_BETWEEN_TASKS = 2         # seconds


def score_virality(video):
    """
    Very lightweight heuristic scorer.

    You can expand this later, but this keeps it stable and predictable:
    - title keywords
    - creator/channel hint
    - engagement stats if available
    """
    title = video.get("title", "").lower()

    score = 0.0

    # 🔥 Keywords that tend to go viral
    hot_terms = [
        "ai", "trump", "breaking", "exposed", "scandal",
        "war", "fail", "secret", "leak", "interview",
        "debate", "urgent", "files", "banned",
        "epstein", "election", "collapse",
    ]
    for term in hot_terms:
        if term in title:
            score += 0.3

    # 🔥 Kyle Kulinski / Secular Talk
    if "kulinski" in title or "secular" in title:
        score += 0.8

    # 🔥 Major news channels = higher amplification potential
    news_channels = [
        "cnn", "bbc", "msnbc", "nbc", "reuters",
        "guardian", "vice", "al jazeera"
    ]
    channel = video.get("channel", "").lower()
    for n in news_channels:
        if n in channel:
            score += 0.5

    # 🔥 Long descriptive titles
    if len(title) > 75:
        score += 0.3

    return round(score, 2)


def run_virality_pass():
    print("=== Leninware YouTube Virality Pass ===")

    try:
        # STEP 1: fetch latest videos from your ingest module
        candidates = get_candidate_videos()
        if not candidates:
            print("No videos returned.")
            return

        print(f"Fetched {len(candidates)} videos.")

        # STEP 2: score everything
        scored = []
        for vid in candidates:
            s = score_virality(vid)
            vid["score"] = s
            scored.append(vid)

            print(f"\nTitle: {vid.get('title')}")
            print(f"URL:   {vid.get('url')}")
            print(f"Score: {s}")

        # STEP 3: choose top videos
        scored.sort(key=lambda v: v["score"], reverse=True)
        top = [v for v in scored if v["score"] >= VIRALITY_THRESHOLD]

        if not top:
            print("\nNo videos crossed virality threshold.")
            return

        # Limit processing
        top = top[:MAX_VIDEOS_TO_PROCESS]

        # STEP 4: process each video through Leninware pipeline
        for vid in top:
            print("\n=== Processing Video ===")
            print(f"URL: {vid['url']}")
            try:
                output = generate_leninware_tts_from_url(vid["url"])
                print("Pipeline output:")
                print(output)
            except Exception as e:
                print(f"Error generating TTS for {vid['url']}")
                traceback.print_exc()

            time.sleep(SLEEP_BETWEEN_TASKS)

        print("\n=== Virality pass complete ===\n")

    except Exception as e:
        print("Worker crashed:")
        traceback.print_exc()