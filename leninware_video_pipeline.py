# leninware_video_pipeline.py
"""
Leninware Video Pipeline

Implements:
1. Fetch YouTube transcript via TranscriptAPI.
2. Generate Leninware commentary using Claude Sonnet-4.
3. (Stub) Render video via Shotstack.
4. (Stub) Upload to YouTube.

Only steps 1 and 2 are fully implemented.
"""

import os
from typing import Optional

import requests
import anthropic

# === API keys ===============================================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")
SHOTSTACK_API_KEY = os.getenv("SHOTSTACK_API_KEY")  # optional, future use

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

MODEL = "claude-sonnet-4-20250514"

# === System prompt ==========================================================

LENINWARE_TTS_SYSTEM = """
SYSTEM: Leninware TTS Mode.
Produce ONE short, viral, Gen-Z aware, ruthless Marxist-Leninist commentary.
Punchy, direct, structured. Avoid academic jargon.

Rules:
- Call out the creator by name when identifiable.
- Replace "Trump" with "Donald".
- Replace "Israel" with "Istate".
- Emphasize class, imperialism, racial capitalism, media co-optation.
- Keep sentence flow tight for TTS rhythm.
- End with: "Real comrades like and subscribe."
"""

# === Transcript fetch =======================================================

def fetch_transcript(video_url: str) -> str:
    endpoint = "https://transcriptapi.com/api/v2/youtube/transcript"
    headers = {"Authorization": f"Bearer {TRANSCRIPT_API_KEY}"}
    params = {"video_url": video_url, "format": "text"}

    resp = requests.get(endpoint, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.text


# === TTS generation =========================================================

def generate_leninware_tts_from_url(video_url: str) -> str:
    print(f"[pipeline] Fetching transcript: {video_url}")
    transcript = fetch_transcript(video_url)

    print("[pipeline] Sending transcript to Claude...")
    msg = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=LENINWARE_TTS_SYSTEM.strip(),
        messages=[{"role": "user", "content": transcript}],
    )

    result = msg.content[0].text
    print("[pipeline] Received Leninware commentary.")
    return result


# === Shotstack placeholder ==================================================

def render_video_with_shotstack(tts_script: str, title: str) -> Optional[str]:
    if not SHOTSTACK_API_KEY:
        print("[pipeline] No SHOTSTACK_API_KEY set. Skipping render.")
        return None

    preview = tts_script[:200].replace("\n", " ")
    print("[pipeline] (stub) Would render video with Shotstack:")
    print(f"  Script preview: {preview}…")
    return None


# === YouTube upload stub ===================================================

def upload_to_youtube_stub(path_or_url: str, title: str, description: str = ""):
    if not path_or_url:
        print("[pipeline] No rendered video to upload.")
        return None

    print("[pipeline] (stub) Would upload to YouTube:")
    print(f"  File/URL: {path_or_url}")
    print(f"  Title: {title}")
    print(f"  Description: {description[:160]}...")
    return None