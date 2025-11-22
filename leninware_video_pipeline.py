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


# ---------------------------
# 1. TRANSCRIPT FETCHER
# ---------------------------
def fetch_transcript(video_url: str) -> str:
    """Get plain-text transcript from TranscriptAPI."""
    endpoint = "https://transcriptapi.com/api/v2/youtube/transcript"
    headers = {"Authorization": f"Bearer {TRANSCRIPT_API_KEY}"}
    params = {"video_url": video_url, "format": "text"}

    resp = requests.get(endpoint, headers=headers, params=params)
    resp.raise_for_status()
    return resp.text.strip()


# ---------------------------
# 2. LENINWARE CLAUDE GENERATOR
# ---------------------------
def generate_leninware_tts_from_url(video_url: str) -> str:
    """Fetch transcript and send to Claude Sonnet-4 for Leninware output."""

    transcript = fetch_transcript(video_url)

    msg = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=LENINWARE_TTS_SYSTEM,
        messages=[
            {"role": "user", "content": transcript}
        ]
    )

    # Claude returns an array of content blocks
    return msg.content[0].text.strip()


# ---------------------------
# 3. IF RUN DIRECTLY, TEST IT
# ---------------------------
if __name__ == "__main__":
    test_url = input("Enter a YouTube URL to test Leninware Sonnet-4:\n> ").strip()
    print("\nFetching transcript…")
    out = generate_leninware_tts_from_url(test_url)
    print("\n===== LENINWARE OUTPUT =====\n")
    print(out)