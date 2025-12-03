# shotstack_renderer.py

import base64
import time
import wave
from contextlib import closing
from typing import List
import textwrap
import requests
import os

from config import USE_MOCK_AI, require_env, SHOTSTACK_API_URL


def _encode_file(path: str) -> str:
    """Return base64 of a file with debug info on failure."""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    except Exception as e:
        print(f"[shotstack] ERROR reading file '{path}': {e}")
        return ""


def _get_wav_duration_seconds(path: str) -> float:
    """Return audio length in seconds; fall back with logs."""
    try:
        with closing(wave.open(path, "rb")) as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            dur = frames / float(rate or 1)
            print(f"[shotstack] Audio duration: {dur:.2f}s")
            return dur
    except Exception as e:
        print(f"[shotstack] ERROR reading WAV duration: {e}")
        return 0.0


def _split_script(script_text: str, num_chunks: int) -> List[str]:
    """Split captions into chunks with debug info."""
    if num_chunks <= 0:
        print("[shotstack] WARNING: num_chunks <= 0, returning entire script once.")
        return [script_text]

    wrapped = textwrap.wrap(script_text.strip(), width=160)
    if not wrapped:
        print("[shotstack] WARNING: Script too short or empty for wrapping.")
        return [""]

    num_chunks = min(num_chunks, len(wrapped))
    approx_size = len(wrapped) // num_chunks

    print(f"[shotstack] Creating {num_chunks} caption chunks "
          f"from {len(wrapped)} wrapped lines.")

    chunks = []
    idx = 0
    for i in range(num_chunks):
        if i == num_chunks - 1:
            group = wrapped[idx:]
        else:
            group = wrapped[idx: idx + approx_size]
        idx += approx_size
        chunks.append(" ".join(group))

    return chunks


def render_video_with_shotstack(
    audio_file: str,
    image_files: List[str],
    script_text: str,
    output_video_path: str,
) -> str:
    """
    Render a video using Shotstack.
    MOCK MODE: Produce a tiny placeholder MP4 instead of doing an API call.
    """

    # ----------------------------------------------------
    # MOCK MODE
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print("[shotstack:mock] Generating placeholder video...")
        dummy_mp4 = (
            b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41"
        )
        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
        with open(output_video_path, "wb") as f:
            f.write(dummy_mp4)
        print("[shotstack:mock] DONE:", output_video_path)
        return output_video_path

    # ----------------------------------------------------
    # REAL SHOTSTACK MODE
    # ----------------------------------------------------
    print("[shotstack] Starting real Shotstack render...")
    api_key = require_env("SHOTSTACK_API_KEY")

    # 1. Compute audio duration
    audio_duration = _get_wav_duration_seconds(audio_file)
    if audio_duration <= 0:
        print("[shotstack] WARNING: Invalid audio duration, using fallback 15s")
        audio_duration = 15.0

    num_images = max(len(image_files), 1)
    segment_length = audio_duration / num_images
    print(f"[shotstack] Rendering {num_images} frames at {segment_length:.2f}s each")

    # 2. Image clips
    image_clips = []
    t = 0.0
    for path in image_files:
        if not os.path.exists(path):
            print(f"[shotstack] WARNING: Missing image file: {path}")
        encoded = _encode_file(path)

        image_clips.append(
            {
                "asset": {
                    "type": "image",
                    "src": f"data:image/png;base64,{encoded}",
                },
                "start": round(t, 3),
                "length": round(segment_length, 3),
                "fit": "contain",
            }
        )
        t += segment_length

    # 3. Caption chunks
    chunks = _split_script(script_text, num_images)
    caption_clips = []
    t = 0.0
    for chunk in chunks:
        caption_clips.append(
            {
                "asset": {
                    "type": "title",
                    "text": chunk,
                    "size": "small",
                    "style": "minimal",
                    "color": "#ffffff",
                },
                "start": round(t, 3),
                "length": round(segment_length, 3),
                "position": "bottom",
            }
        )
        t += segment_length

    # 4. Payload assembly
    payload = {
        "timeline": {
            "background": "#000000",
            "soundtrack": {
                "src": f"data:audio/wav;base64,{_encode_file(audio_file)}",
                "effect": "fadeIn",
            },
            "tracks": [
                {"clips": image_clips},
                {"clips": caption_clips},
            ],
        },
        "output": {
            "format": "mp4",
            "resolution": "1080",
        },
    }

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    # 5. Submit render
    print("[shotstack] Submitting render job...")
    try:
        resp = requests.post(SHOTSTACK_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        print("[shotstack] Render job accepted.")
    except Exception as e:
        print("[shotstack] ERROR submitting job:", e)
        raise

    data = resp.json()
    if "response" not in data or "id" not in data["response"]:
        print("[shotstack] ERROR: Unexpected Shotstack response:", data)
        raise RuntimeError("Invalid Shotstack response")

    render_id = data["response"]["id"]
    status_url = f"{SHOTSTACK_API_URL}/{render_id}"
    print(f"[shotstack] Render ID: {render_id}")

    # 6. Poll with timeout
    timeout = time.time() + 60 * 10  # 10 minutes
    attempt = 0

    while True:
        attempt += 1
        if time.time() > timeout:
            raise TimeoutError("[shotstack] ERROR: Render timed out after 10 minutes.")

        try:
            status = requests.get(status_url, headers=headers).json()
        except Exception as e:
            print("[shotstack] ERROR polling status:", e)
            time.sleep(3)
            continue

        s = status.get("response", {}).get("status", "unknown")
        print(f"[shotstack] Poll #{attempt}: Status = {s}")

        if s == "done":
            url = status["response"]["url"]
            print("[shotstack] DONE — Downloading final video...")
            break

        if s in ("failed", "errored"):
            print("[shotstack] ERROR: Render failed:", status)
            raise RuntimeError(f"Shotstack render failed: {status}")

        time.sleep(3)

    # 7. Download final video
    try:
        video_bytes = requests.get(url).content
        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
        with open(output_video_path, "wb") as f:
            f.write(video_bytes)
        print("[shotstack] Video saved:", output_video_path)
    except Exception as e:
        print("[shotstack] ERROR downloading final video:", e)
        raise

    return output_video_path