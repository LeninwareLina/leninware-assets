import time
import requests
from config import require_env, SHOTSTACK_API_URL


def render_video_with_shotstack(audio_file: str, output_video_path: str) -> str:
    """
    Render a simple video using Shotstack Edit API.
    Returns path to rendered MP4 file.
    """

    api_key = require_env("SHOTSTACK_API_KEY")

    # Basic template: black background + audio track
    payload = {
        "timeline": {
            "soundtrack": {
                "src": f"data:audio/wav;base64,{_encode_file(audio_file)}",
                "effect": "fadeIn"
            },
            "background": "#000000",
            "tracks": []
        },
        "output": {
            "format": "mp4",
            "resolution": "1080"
        }
    }

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    # Submit the render request
    resp = requests.post(
        SHOTSTACK_API_URL,
        json=payload,
        headers=headers,
        timeout=20
    )
    resp.raise_for_status()

    render_id = resp.json()["response"]["id"]

    # Poll until the video is finished
    status_url = f"{SHOTSTACK_API_URL}/{render_id}"
    while True:
        status = requests.get(status_url, headers=headers).json()
        state = status["response"]["status"]

        if state == "done":
            url = status["response"]["url"]
            break
        elif state in ("failed", "errored"):
            raise RuntimeError(f"Shotstack render failed: {status}")

        time.sleep(3)

    # Download rendered MP4
    video_bytes = requests.get(url).content
    with open(output_video_path, "wb") as f:
        f.write(video_bytes)

    return output_video_path


def _encode_file(path: str) -> str:
    """Base64 encode a file for Shotstack upload."""
    import base64
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")