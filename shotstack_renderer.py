# shotstack_renderer.py

from typing import List, Optional
import json
import requests

from config import SHOTSTACK_API_KEY


SHOTSTACK_ENDPOINT = "https://api.shotstack.io/v1/render"


def render_video_with_shotstack(
    audio_path: Optional[str],
    image_paths: List[str],
    title: str,
) -> Optional[str]:
    """
    Placeholder Shotstack integration.

    Right now this just logs what it WOULD do. If SHOTSTACK_API_KEY is set,
    it posts a very minimal JSON and prints the response. You will still need
    to refine the template for real production use.
    """
    if not SHOTSTACK_API_KEY:
        print("[shotstack] SHOTSTACK_API_KEY not set; skipping render.")
        return None

    if not image_paths:
        print("[shotstack] No images provided; skipping render.")
        return None

    print("[shotstack] (stub) Would render video with:")
    print(f"  Title: {title}")
    print(f"  Images: {image_paths}")
    if audio_path:
        print(f"  Audio: {audio_path}")

    # TODO: Replace with real Shotstack timeline/edit JSON.
    # For now just do a noop POST to show wiring.
    headers = {
        "x-api-key": SHOTSTACK_API_KEY,
        "Content-Type": "application/json",
    }
    dummy_payload = {"data": "leninware stub render"}
    try:
        resp = requests.post(SHOTSTACK_ENDPOINT, headers=headers, data=json.dumps(dummy_payload), timeout=20)
        print(f"[shotstack] Response status: {resp.status_code}")
        print(f"[shotstack] Body: {resp.text[:200]}...")
    except Exception as e:
        print(f"[shotstack] Error calling Shotstack: {e}")

    # Return None until you wire real rendering logic
    return None