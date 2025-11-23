# youtube_uploader.py

from typing import Optional

from config import (
    YOUTUBE_UPLOAD_CLIENT_ID,
    YOUTUBE_UPLOAD_CLIENT_SECRET,
    YOUTUBE_UPLOAD_REFRESH_TOKEN,
)


def upload_video_stub(
    video_path: str,
    title: str,
    description: str = "",
) -> Optional[str]:
    """
    Placeholder for YouTube upload.

    Right now this just logs what it WOULD do.
    A real upload requires google-api-python-client and OAuth.

    Returning None so pipeline doesn't crash.
    """
    if not (YOUTUBE_UPLOAD_CLIENT_ID and YOUTUBE_UPLOAD_CLIENT_SECRET and YOUTUBE_UPLOAD_REFRESH_TOKEN):
        print("[youtube_upload] OAuth creds not set; skipping upload.")
        print(f"[youtube_upload] Would upload: {video_path} | title={title}")
        return None

    print("[youtube_upload] Upload stub; real implementation not yet wired.")
    print(f"  Video: {video_path}")
    print(f"  Title: {title}")
    if description:
        print(f"  Description: {description[:150]}...")
    return None