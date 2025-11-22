# youtube_ingest.py
#
# Leninware Viral Discovery Engine (v2)
# Scrapes highly-viral political channels + keyword trending.

import os
import requests
from googleapiclient.discovery import build

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY not found in environment variables.")

yt = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


############################################################
# 1. HIGH-VIRALITY POLITICAL CHANNELS (SHORTS HEAVY)
############################################################

HIGH_VIRAL_CHANNELS = [
    # Left commentary clips
    "UCJdKr0Bgd_5saZYqLCa9mng",  # Pakman Clips
    "UCX7dCJz6Fr7HabVt5dLJ4gQ",  # MeidasTouch Shorts
    "UCZV8p0kB6k2Jf85sHft8ZSw",  # Farron Cousins Clips
    "UC6eYbBvIwq9VXYg7Wc6AtAw",  # Breaking Points Clips

    # Right-wing viral outrage
    "UCx6h-dHQG2fE9AmlFWWlZug",  # Shapiro Shorts
    "UC0uVZd8N7cqZvP7Vmbg-h5w",  # Tim Pool Clips
    "UCjGMDjhrOrN3i_yS4bTrZHA",  # Jordan Peterson Clips
    "UC0v-tlzsn0QZwJnkiaUSJVQ",  # PragerU Shorts

    # Debate/influencer
    "UC554eY5jNUfDq3yDOJYirOQ",  # HasanAbi Clips
    "UC0rE2qqzdGdP9TI-ZXY2xjw",  # Destiny Clips
    "UCdJ9oJ2Guf8v9lCWdnmCyIw",  # H3 Podcast Clips

    # Misc viral political/tiktok repost channels
    "UC_6Wk2kJ1L3edQY12znl5sA",  # PatriotTakes
    "UCG8rbF3g2AMX70yOd8vqIZg",  # More Perfect Union
    "UCU9YqkZk_9D_q7D1uUM7ogg",  # TikTok Politics Compilations
]


############################################################
# Fetch recent uploads from these channels
############################################################

def fetch_recent_from_channels(max_results=15):
    all_videos = []

    for channel_id in HIGH_VIRAL_CHANNELS:
        try:
            search = yt.search().list(
                part="snippet",
                channelId=channel_id,
                order="date",
                type="video",
                maxResults=max_results
            ).execute()

            for item in search.get("items", []):
                vid = item["id"]["videoId"]
                title = item["snippet"]["title"]

                all_videos.append({
                    "title": title,
                    "video_id": vid,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "views": None,
                    "published": item["snippet"]["publishedAt"]
                })
        except Exception as e:
            print(f"Error fetching channel {channel_id}: {e}")

    return all_videos


############################################################
# 2. TRENDING SEARCH TERMS (Political hot zones)
############################################################

HOT_KEYWORDS = [
    "Trump", "Donald", "Biden", "election", "fascist",
    "Istate", "Gaza", "genocide", "Ukraine",
    "debate", "hearing", "indictment", "Congress",
    "breaking news", "protest", "ruling", "speech"
]

def keyword_trending(max_per_keyword=5):
    results = []

    for keyword in HOT_KEYWORDS:
        try:
            search = yt.search().list(
                part="snippet",
                q=keyword,
                type="video",
                order="relevance",
                maxResults=max_per_keyword
            ).execute()

            for item in search.get("items", []):
                vid = item["id"]["videoId"]
                results.append({
                    "title": item["snippet"]["title"],
                    "video_id": vid,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "views": None,
                    "published": item["snippet"]["publishedAt"]
                })
        except Exception as e:
            print(f"Keyword fetch error ({keyword}): {e}")

    return results


############################################################
# 3. VIDEO DETAIL ENRICHMENT
############################################################

def enrich_video_details(video_list):
    for vid in video_list:
        try:
            meta = yt.videos().list(
                part="statistics",
                id=vid["video_id"]
            ).execute()

            stats = meta["items"][0]["statistics"]
            vid["views"] = int(stats.get("viewCount", 0))

        except Exception as e:
            print(f"Error enriching {vid['video_id']}: {e}")

    return video_list


############################################################
# PUBLIC ENTRY POINT (USED BY THE VIRALITY WORKER)
############################################################

def get_candidate_videos():
    """
    Returns a combined list of:
    - Latest videos from high-virality channels
    - Keyword-based political trending
    - All enriched with view counts
    """

    print("Fetching from high-virality channels…")
    ch = fetch_recent_from_channels()

    print("Fetching from keyword trending…")
    kw = keyword_trending()

    combined = ch + kw
    print(f"Total candidates fetched: {len(combined)}")

    print("Enriching metadata…")
    enriched = enrich_video_details(combined)

    enriched.sort(key=lambda x: x["views"] or 0, reverse=True)

    return enriched