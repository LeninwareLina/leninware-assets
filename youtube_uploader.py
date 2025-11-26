# youtube_uploader.py

from typing import Optional


def upload_video_to_youtube(video_path: str, title: str, description: str) -> Optional[str]:
    """
    Stub for uploading the rendered video back to YouTube.

    Returns a video_id or None.

    Implement this with the YouTube Data API if/when you're ready.
    """
    print(f"[uploader] Would upload {video_path} with title='{title}'")
    return None