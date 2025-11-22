# youtube_ingest.py
#
# Returns a list of recent videos from selected channels.
# Output format is fully compatible with youtube_virality_worker.py

import os
import requests

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Channels Leninware should extract content from
CHANNEL_IDS = {
    "BBC News": "UC16niRr50-MSBwiO3YDb3RA",
    "CNN": "UCupvZG-5ko_eiXAupbDfxWw",
    "MeidasTouch": "UC_Vf4nY8mko7VaFqx2g3Tdw",
    "Secular Talk": "UCldfgbzNILYZA4dmDt4Cd6A",
    "The Majority Report": "UCpYCxV51bykhMY-wsu9nq4g",
    "MSNBC": "UCaXkIU1QidjPwiAYu6GcHjg"
}

def fetch_recent_videos(max_results=10):
    """
    Fetch recent uploads from the target channels.
    Returns list[dict] with required metadata for virality scoring.
    """
    videos = []

    for channel_name, channel_id in CHANNEL_IDS.items():
        try:
            search_url = (
                "https://www.googleapis.com/youtube/v3/search?"
                f"key={YOUTUBE_API_KEY}"
                f"&channelId={channel_id}"
                f"&part=snippet"
                f"&order=date"
                f"&maxResults={max_results}"
            )
            resp = requests.get(search_url)
            data = resp.json()

            for item in data.get("items", []):
                video_id = item["id"].get("videoId")
                if not video_id:
                    continue

                video_url = f"https://www.youtube.com/watch?v={video_id}"

                video_info = {
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "url": video_url,
                    "channel_title": channel_name,
                    "tags": [],
                    "published_at": item["snippet"].get("publishedAt"),
                }

                videos.append(video_info)

        except Exception as e:
            print(f"Error fetching videos for {channel_name}: {e}")

    return videos


# Alias to match expected function names
get_recent_videos = fetch_recent_videos
get_candidate_videos = fetch_recent_videos