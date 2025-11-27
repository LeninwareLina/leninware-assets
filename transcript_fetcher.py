import os
import json
import time
import datetime
import requests

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CACHE_FILE = "seen_videos.json"

CHANNELS = [
    "UCXIJgqnII2ZOINSWNOGFThA",  # Fox News
    "UCaXkIU1QidjPwiAYu6GcHjg",  # MSNBC
    "UC6oQ7Oq9WgMt5NL3SF3xC4Q",  # CNN
]

SAVE_THRESHOLD = 3  # Your scoring system threshold


# -----------------------------------------------------------
#  LOAD CACHE
# -----------------------------------------------------------
def load_cache():
    if not os.path.exists(CACHE_FILE):
        return set()
    try:
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


# -----------------------------------------------------------
#  SAVE CACHE
# -----------------------------------------------------------
def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(cache), f)


# -----------------------------------------------------------
#  CHECK YOUTUBE QUOTA BEFORE ANYTHING ELSE
# -----------------------------------------------------------
def quota_test():
    test_url = f"https://www.googleapis.com/youtube/v3/videos?part=id&id=invalid123&key={YOUTUBE_API_KEY}"
    r = requests.get(test_url)
    if "error" in r.json():
        reason = r.json()["error"]["errors"][0]["reason"]
        print(f"[QUOTA CHECK] YouTube API error: {reason}")
        if reason in ["quotaExceeded", "dailyLimitExceeded"]:
            return False
    return True


# -----------------------------------------------------------
#  FETCH LATEST VIDEOS FOR A CHANNEL
# -----------------------------------------------------------
def fetch_channel_uploads(channel_id):
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?key={YOUTUBE_API_KEY}&channelId={channel_id}"
        "&part=snippet&type=video&order=date&maxResults=5"
    )
    r = requests.get(url)
    data = r.json()

    if "error" in data:
        reason = data["error"]["errors"][0]["reason"]
        print(f"[INGESTER] ERROR fetching channel {channel_id}: {reason}")
        return []

    videos = []
    for item in data.get("items", []):
        vid = item["id"]["videoId"]
        title = item["snippet"]["title"]
        published = item["snippet"]["publishedAt"]
        videos.append((vid, title, published))

    return videos


# -----------------------------------------------------------
#  MAIN INGESTER LOGIC
# -----------------------------------------------------------
def main():
    print("=== SAFE INGESTER START ===")

    if not quota_test():
        print("[INGESTER] ABORT — YouTube quota exceeded.")
        return

    cache = load_cache()
    print(f"[CACHE] Loaded {len(cache)} previously seen videos.")

    new_candidates = []

    for channel in CHANNELS:
        print(f"[CHANNEL] Checking uploads for: {channel}")

        videos = fetch_channel_uploads(channel)

        for video_id, title, published in videos:
            if video_id in cache:
                print(f"  - Skipping already-seen video: {video_id}")
                continue

            print(f"  + NEW video: {video_id} — {title}")
            new_candidates.append({
                "video_id": video_id,
                "title": title,
                "channel": channel,
                "published": published,
                "score": 5  # always high enough so they pass to the worker
            })
            cache.add(video_id)

    save_cache(cache)

    print(f"[RESULT] New candidates found: {len(new_candidates)}")

    # Output for worker
    print(json.dumps(new_candidates))

    print("=== SAFE INGESTER COMPLETE ===")


if __name__ == "__main__":
    main()