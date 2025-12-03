# youtube_uploader.py

from typing import List, Optional

from config import USE_MOCK_AI, require_env

# Only import Google APIs if NOT in mock mode
if not USE_MOCK_AI:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _get_youtube_client():
    """Build an authenticated YouTube client using OAuth refresh token."""

    # ✔ FIXED: match config.py variable names exactly
    client_id = require_env("GOOGLE_CLIENT_ID")
    client_secret = require_env("GOOGLE_CLIENT_SECRET")
    refresh_token = require_env("GOOGLE_REFRESH_TOKEN")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret,
        scopes=[YOUTUBE_UPLOAD_SCOPE],
    )

    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: str,
    title: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    privacy_status: str = "public",
) -> str:
    """
    Upload a video file to YouTube.

    MOCK MODE:
        - Skip upload entirely
        - Return fake video ID
        - Do NOT require OAuth or Google credentials
    """

    # ----------------------------------------------------
    # MOCK MODE — skip YouTube upload
    # ----------------------------------------------------
    if USE_MOCK_AI:
        fake_id = "MOCK_VIDEO_ID_12345"
        print(f"[upload:mock] Skipping YouTube upload. Returning fake ID: {fake_id}")
        return fake_id

    # ----------------------------------------------------
    # REAL MODE — upload to YouTube
    # ----------------------------------------------------
    youtube = _get_youtube_client()

    body = {
        "snippet": {
            "title": title,
            "description": description,
        },
        "status": {
            "privacyStatus": privacy_status,
        },
    }

    if tags:
        body["snippet"]["tags"] = tags

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[upload] Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print(f"[upload] Video uploaded. ID: {video_id}")
    return video_id