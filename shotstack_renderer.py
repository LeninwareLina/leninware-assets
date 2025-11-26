# shotstack_renderer.py

from typing import List, Optional
import json
import requests

from config import SHOTSTACK_API_KEY, SHOTSTACK_BASE_URL, require_env


def render_video_with_shotstack(
    audio_path: Optional[str],
    image_paths: List[str],
    title: str,
) -> Optional[str]:
    """
    Submit a simple slideshow-style render to Shotstack.

    Returns:
        render_id or None (on failure).

    This is deliberately minimal and defensive.
    """

    if not image_paths:
        print("[shotstack] No images provided; skipping render.")
        return None

    api_key = require_env("SHOTSTACK_API_KEY", SHOTSTACK_API_KEY)
    base_url = require_env("SHOTSTACK_BASE_URL", SHOTSTACK_BASE_URL)

    # Very simple timeline: single track of images, each ~3 seconds.
    clips = []
    for i, path in enumerate(image_paths):
        clips.append(
            {
                "asset": {
                    "type": "image",
                    "src": path,
                },
                "start": i * 3,
                "length": 3,
            }
        )

    timeline = {
        "tracks": [
            {
                "clips": clips,
            }
        ],
        "soundtrack": {
            "src": audio_path,
            "effect": "fadeInFadeOut",
        }
        if audio_path
        else None,
    }

    payload = {
        "timeline": timeline,
        "output": {
            "format": "mp4",
            "resolution": "sd",
            "fps": 25,
        },
    }

    # Clean out None values
    def _strip_none(obj):
        if isinstance(obj, dict):
            return {k: _strip_none(v) for k, v in obj.items() if v is not None}
        if isinstance(obj, list):
            return [_strip_none(v) for v in obj]
        return obj

    payload = _strip_none(payload)

    print("[shotstack] Payload:", json.dumps(payload, indent=2))

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            base_url,
            headers=headers,
            json=payload,
            timeout=30,
        )
    except Exception as e:
        print(f"[shotstack] Request error: {e}")
        return None

    if resp.status_code not in (200, 201):
        print(f"[shotstack] Error {resp.status_code}: {resp.text}")
        return None

    try:
        data = resp.json()
    except Exception:
        print("[shotstack] Non-JSON response:", resp.text)
        return None

    render_id = data.get("response", {}).get("id") or data.get("id")
    print(f"[shotstack] Render queued, id={render_id}")
    return render_id