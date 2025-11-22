# leninware_video_pipeline.py
"""
Leninware video pipeline:

1. Fetch transcript for a YouTube video using TranscriptAPI.
2. Send transcript to Claude Sonnet-4 with the Leninware TTS system prompt.
3. (Hook) Optionally render a video via Shotstack.
4. (Hook) Optionally upload rendered video to YouTube.

Only steps 1 & 2 are fully implemented. Shotstack + upload are provided as
stubs with clear TODOs so you can wire in credentials and templates later.
"""

import os
from typing import Optional

import requests
import anthropic

# === API keys ===============================================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")
SHOTSTACK_API_KEY = os.getenv("SHOTSTACK_API_KEY")  # optional, for later

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

MODEL = "claude-sonnet-4-20250514"

LENINWARE_TTS_SYSTEM = """
SYSTEM: Leninware TTS Mode.
Produce ONE short, viral, Gen-Z aware, ruthless Marxist-Leninist commentary.
Punchy, direct, structurally sharp. No academic jargon. No both-sides. No moralizing.

Rules:
- Call out the creator by name if it’s clear from the transcript.
- Replace “Trump” with “Donald”.
- Replace “Israel” with “Istate”.
- Focus on class, imperialism, racial capitalism, and media co-optation.
- Assume this will be read by a TTS voice, so keep sentences tight and rhythmic.
- Always end with: “Real comrades like and subscribe.”
"""


# === Transcript step ========================================================

def fetch_transcript(video_url: str) -> str:
    """Get plain-text transcript from TranscriptAPI."""
    endpoint = "https://transcriptapi.com/api/v2/youtube/transcript"
    headers = {"Authorization": f"Bearer {TRANSCRIPT_API_KEY}"}
    params = {"video_url": video_url, "format": "text"}

    resp = requests.get(endpoint, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.text


# === Claude step ============================================================

def generate_leninware_tts_from_url(video_url: str) -> str:
    """
    High-level helper: given a YouTube URL, fetch the transcript and generate
    a Leninware-style TTS script using Claude Sonnet-4.
    """
    print(f"[leninware_pipeline] Fetching transcript for: {video_url}")
    transcript = fetch_transcript(video_url)

    print("[leninware_pipeline] Sending transcript to Claude Sonnet-4...")
    msg = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=LENINWARE_TTS_SYSTEM.strip(),
        messages=[
            {
                "role": "user",
                "content": transcript,
            }
        ],
    )

    text = msg.content[0].text
    print("[leninware_pipeline] Received Leninware TTS script.")
    return text


# === Shotstack hook (stub for now) =========================================

def render_video_with_shotstack(
    tts_script: str,
    title: str,
) -> Optional[str]:
    """
    Placeholder for Shotstack integration.

    Right now this ONLY logs what it would do and returns None.

    TODO when you're ready:
    - Use the Shotstack REST API or Python SDK.
    - Build a simple template that:
        * uses your TTS audio file (once OpenAI audio is wired in),
        * adds background footage or images,
        * overlays subtitles/captions.
    - POST the 'edit' JSON to Shotstack and poll for a completed render URL.

    Return:
        The public URL or file path of the rendered video, or None if skipped.
    """
    if not SHOTSTACK_API_KEY:
        print("[leninware_pipeline] SHOTSTACK_API_KEY not set; "
              "skipping Shotstack render.")
        return None

    # For now we just log the first part of the script so you know it ran.
    preview = tts_script[:200].replace("\n", " ")
    print("[leninware_pipeline] (stub) Would render Shotstack video with script:")
    print(f"  “{preview}...”")
    # Return None until you wire in real rendering
    return None


# === YouTube upload hook (stub for now) ====================================

def upload_to_youtube_stub(
    rendered_video_path_or_url: str,
    title: str,
    description: str = "",
) -> Optional[str]:
    """
    Placeholder for YouTube upload.

    Important: an API key alone is NOT enough to upload videos. YouTube
    uploads require an OAuth2 client and a refresh token for your channel.

    This stub just logs what it would do.

    Once you’re ready, you can:
    - Run a one-time OAuth flow on your laptop to get a refresh token.
    - Store that safely (e.g., Railway variable).
    - Use google-api-python-client to perform uploads from the server.

    Return:
        The YouTube video id or URL, or None.
    """
    if not rendered_video_path_or_url:
        print("[leninware_pipeline] No rendered video to upload; skipping.")
        return None

    print("[leninware_pipeline] (stub) Would upload rendered video to YouTube:")
    print(f"  Source: {rendered_video_path_or_url}")
    print(f"  Title: {title}")
    if description:
        print(f"  Description: {description[:160]}...")

    return None  # nothing actually uploaded yet