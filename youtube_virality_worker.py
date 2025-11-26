from youtube_ingest import get_candidate_videos
from transcript_fetcher import fetch_transcript
from leninware_commentary import generate_leninware_commentary


def score_video(item) -> float:
    """Quick heuristic score system."""
    title = item["snippet"]["title"].lower()
    score = 0

    if "breaking" in title:
        score += 3
    if "news" in title:
        score += 2
    if "trump" in title:
        score += 2
    if "live" in title:
        score -= 1

    return score


def run_virality_pass():
    candidates = get_candidate_videos()

    print(f"[worker] Found {len(candidates)} candidates")

    # Score and filter
    processed = []
    for item in candidates:
        score = score_video(item)
        if score >= 3:
            processed.append((item, score))

    print(f"[worker] {len(processed)} videos crossed threshold.")

    # Process high-score videos
    for item, score in processed:
        url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        print("\n=== Processing candidate ===")
        print(f"Channel: {channel}")
        print(f"Title: {title}")
        print(f"URL: {url}")
        print(f"Score: {score}")

        # Fetch transcript
        try:
            transcript = fetch_transcript(url)
        except Exception as e:
            print(f"[worker] Transcript fetch failed: {e}")
            continue

        # Generate commentary
        commentary = generate_leninware_commentary(transcript)
        print("[worker] Commentary generated.")
        print(commentary)