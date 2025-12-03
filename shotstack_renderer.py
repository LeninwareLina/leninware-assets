# shotstack_renderer.py

import base64
import time
import wave
from contextlib import closing
from typing import List
import textwrap
import requests

from config import require_env, SHOTSTACK_API_URL


def _encode_file(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _get_wav_duration_seconds(path: str) -> float:
    with closing(wave.open(path, "rb")) as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate or 1)


def _split_script(script_text: str, num_chunks: int) -> List[str]:
    """
    Wrap text to avoid extremely long lines, then chunk
    into roughly equal groups for caption timing.
    """
    if num_chunks <= 0:
        return [script_text]

    wrapped = textwrap.wrap(script_text.strip(), width=160)
    if not wrapped:
        return [""]

    # Cap number of chunks to number of wrapped lines
    num_chunks = min(num_chunks, len(wrapped))
    approx_size = len(wrapped) // num_chunks

    chunks = []
    idx = 0
    for i in range(num_chunks):
        if i == num_chunks - 1:
            group = wrapped[idx:]
        else:
            group = wrapped[idx : idx + approx_size]
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
    Render a video using Shotstack with:
    - TTS audio
    - Image sequence
    - Captions synced to total length
    """
    api_key = require_env("SHOTSTACK_API_KEY")

    # 1. Audio duration
    audio_duration = _get_wav_duration_seconds(audio_file)
    if audio_duration <= 0:
        audio_duration = 15.0  # fallback

    num_images = max(len(image_files), 1)
    segment_length = audio_duration / num_images

    # 2. Image clips
    image_clips = []
    t = 0.0
    for path in image_files:
        image_clips.append(
            {
                "asset": {
                    "type": "image",
                    "src": f"data:image/png;base64,{_encode_file(path)}",
                },
                "start": round(t, 3),
                "length": round(segment_length, 3),
                "fit": "contain",
            }
        )
        t += segment_length

    # 3. Caption chunks (same count as images)
    caption_clips = []
    chunks = _split_script(script_text, num_images)

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

    # 4. Shotstack payload
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

    print("[shotstack] Submitting render...")
    resp = requests.post(SHOTSTACK_API_URL, json=payload, headers=headers)
    resp.raise_for_status()

    render_id = resp.json()["response"]["id"]
    status_url = f"{SHOTSTACK_API_URL}/{render_id}"

    # 5. Poll until done
    while True:
        status = requests.get(status_url, headers=headers).json()
        s = status["response"]["status"]

        if s == "done":
            url = status["response"]["url"]
            print("[shotstack] Rendering complete. Downloading video...")
            break

        if s in ("failed", "errored"):
            raise RuntimeError(f"Shotstack render failed: {status}")

        print(f"[shotstack] Status: {s}... waiting...")
        time.sleep(3)

    # 6. Download final MP4
    video_bytes = requests.get(url).content
    with open(output_video_path, "wb") as f:
        f.write(video_bytes)

    return output_video_path