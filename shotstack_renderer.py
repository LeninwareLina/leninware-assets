# shotstack_renderer.py
import requests
import json

from config import SHOTSTACK_API_KEY, SHOTSTACK_BASE_URL, require_env


def render_video_with_shotstack(video_assets: dict) -> str:
    """
    Sends a render request to Shotstack.

    Args:
        video_assets: dict containing video, audio, and overlays.

    Returns:
        The Shotstack render URL (string).

    Raises:
        RuntimeError if the API call fails.
    """

    api_key = SHOTSTACK_API_KEY
    url = SHOTSTACK_BASE_URL

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, headers=headers, data=json.dumps(video_assets), timeout=30)
    except Exception as e:
        raise RuntimeError(f"Shotstack request error: {e}")

    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"Shotstack error {resp.status_code}: {resp.text}"
        )

    data = resp.json()

    # Extract render URL
    try:
        render_url = data["response"]["url"]
    except Exception:
        raise RuntimeError(f"Unexpected Shotstack response: {data}")

    return render_url