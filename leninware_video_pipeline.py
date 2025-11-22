# leninware_video_pipeline.py

import os
import requests
import anthropic

# Load API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

MODEL = "claude-sonnet-4-20250514"

LENINWARE_TTS_SYSTEM = """
SYSTEM: Leninware TTS Mode.
Produce **one** short, viral, Gen-Z aware, ruthless Marxist-Leninist commentary.
Punchy. Direct. No academic talk. No both-sides. No moralizing.
Call out the creator by name when clear from transcript.
Replace "Trump" with "Donald" and "Israel" with "Istate."
Always end with: "Real comrades like and subscribe."
"""


def fetch_transcript(video_url: str) -> str:
    """Get plain-text transcript from TranscriptAPI."""
    endpoint = "https://transcriptapi.com/api/v2/youtube/transcript"
    headers = {"Authorization": f"Bearer {TRANSCRIPT_API_KEY}"}
    params = {"video_url": video_url, "format": "text"}

    resp = requests.get