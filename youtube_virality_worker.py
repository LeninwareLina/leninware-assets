# youtube_virality_worker.py
#
# Leninware Viral Scanner:
# Fetch candidate videos → LLM virality scoring → forward best video to pipeline.

import os
import time
from datetime import datetime
import traceback

import anthropic
from youtube_ingest import get_candidate_videos
from leninware_video_pipeline import generate_leninware_tts_from_url


# Load API key
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

MODEL = "claude-sonnet-4-20250514"


############################################################
# VIRALITY PROMPT — tuned for “we want stuff Leninware can wreck”
############################################################

VIRALITY_PROMPT = """
You are the Leninware Virality Engine.

Score the following YouTube video for *viral potential* based on these factors:
- High emotional charge (rage, scandal, shock, hypocrisy)
- Clear political narrative
- Culture war triggers
- Strong personalities (creators, politicians, pundits)
- Clip-worthy punchlines or meltdown moments
- Timeliness (recent news, fresh conflict)
- Clear ideological tension

Score from 0.0 to 5.0:
- 0–1: Dead content
- 1–2: Mildly interesting
- 2–3: Trending potential
- 3–4: Reliable viral spark
- 4–5: Highly explosive, perfect for Leninware commentary

Return only this JSON structure:
{
  "score": <float>,
  "reason": "<short explanation>"
}
"""

############################################################
# Ask Sonnet-4 to score virality
############################################################

def score_virality(title, views):
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=VIRALITY_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Title: {title}\nViews: {views}"
            }]
        )

        text = msg.content[0].text.strip()

        # Try to parse JSON safely
        import json
        data = json.loads(text)
        return float(data["score"]), data["reason"]

    except Exception as e:
        print(f"Failed to score virality: {e}")
        print("Raw response:", text)
        return 0.0, "Error parsing response"


############################################################
# MAIN WORKER LOOP
############################################################

def run_worker():
    print("=== Leninware YouTube Virality Worker ===")

    while True:
        print("\n=== Fetching candidates ===")
        try:
            videos = get_candidate_videos()
        except Exception as e:
            print("Error fetching videos from youtube_ingest:")
            traceback.print_exc()
            time.sleep(60)
            continue

        best_video = None
        best_score = -1

        print(f"Got {len(videos)} candidates\n")

        for vid in videos:
            title = vid["title"]
            url = vid["url"]
            views = vid["views"] or 0

            print(f"Title: {title}")
            print(f"URL:   {url}")
            print(f"Views: {views}")

            score, reason = score_virality(title, views)

            print(f"Score: {score:.2f}")
            print(f"Reason: {reason}\n")

            if score > best_score:
                best_score = score
                best_video = vid

        if best_video is None:
            print("No videos found at all — strange. Sleeping.")
            time.sleep(60)
            continue

        # THRESHOLD
        THRESHOLD = 2.2

        print("\n=== BEST CANDIDATE ===")
        print(best_video["title"])
        print(best_video["url"])
        print(f"Score: {best_score:.2f}")

        if best_score >= THRESHOLD:
            print("\n>>> VIRAL ENOUGH. Sending to Leninware TTS engine…\n")

            try:
                generate_leninware_tts_from_url(best_video["url"])
                print(">>> Leninware TTS pipeline completed.\n")
            except Exception as e:
                print("Error running TTS pipeline:")
                traceback.print_exc()
        else:
            print("\nNot viral enough. Nothing sent to Leninware this cycle.\n")

        print(f"Sleeping 20 minutes… (Time: {datetime.utcnow()} UTC)\n")
        time.sleep(20 * 60)
if __name__ == "__main__":
    print("=== DRY TEST ===")
    print("Fetching videos but NOT sending anything to Leninware…\n")

    videos = get_candidate_videos()
    print(f"Found {len(videos)} videos\n")

    for vid in videos:
        print(f"Title: {vid['title']}")
        print(f"URL:   {vid['url']}")
        print(f"Views: {vid['views']}")
        print("---")

    print("\nNow testing virality scoring on FIRST video only:\n")

    if videos:
        title = videos[0]['title']
        views = videos[0]['views']
        score, reason = score_virality(title, views)
        print(f"Score: {score}")
        print(f"Reason: {reason}")