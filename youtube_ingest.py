# youtube_ingest.py

from typing import List, Dict, Any
import datetime as dt

from config import YOUTUBE_API_KEY


def get_candidate_videos() -> List[Dict[str, Any]]:
    """
    Return a list of candidate videos to analyze.

    Shape:
        {
          "url": str,
          "title": str,
          "channel": str,
          "views": int,
          "likes": int,
          "comments": int,
        }

    For now, this is a stub you can replace with real YouTube API calls.
    """
    # If no API key is set, just return an empty list and don't crash.
    if not YOUTUBE_API_KEY:
        print("[ingest] YOUTUBE_API_KEY not set; returning no candidates.")
        return []

    # TODO: implement real ingest using YouTube Data API.
    # For now you can manually plug in test videos here while developing.
    print("[ingest] Stub ingest: override with real YouTube API calls.")
    return []