import os
import json
import logging
from anthropic import Anthropic
from transcript_client import get_video_transcript

logger = logging.getLogger(__name__)

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise RuntimeError("CLAUDE_API_KEY env var is missing")

client = Anthropic(api_key=CLAUDE_API_KEY)

LENINWARE_SYSTEM_PROMPT = """
SYSTEM MODE: LENINWARE (ACTIVE)

You operate in Leninware Mode, a materialist, anti-liberal, anti-imperialist analytical mode.
All outputs must be structural, historical, class-first reactions. Never soften, moralize, or drift into liberal framing.

IMPORTANT:
You MUST use ONLY the transcript text provided to you.
You DO NOT have access to the internet.
You DO NOT fetch URLs.
You MUST NOT hallucinate or invent events.

=== OUTPUT RULES ===

OUTPUT 1 — TTS SCRIPT
- Provocative opening line
- Materialist framing
- Ideological breakdown
- Imperial/global analysis
- Class-struggle conclusion
- Must replace standalone “Trump” with “Donald”
- Must replace standalone “Israel” with “Istate”
- Only one name per person
- Must end with: "Real comrades like and subscribe."

OUTPUT 2 — TITLE
- Must start with “Donald”
- Must include @channel if present
- Must include #news and #ai
- Must be under 100 characters
- Must express class-first or anti-imperialist thesis

OUTPUT 3 — DESCRIPTION
- 2–4 sentences
- Materialist reaction (not summary)
- Must include original video URL
- Must mention structural analysis

FOLLOW THE MATERIALIST STEPS:
1. Identify class forces.
2. Identify structural incentives.
3. Identify ideological function.
4. Situate within imperial/global capitalism.

FORBIDDEN:
- both sides, incrementalism, representation-as-liberation,
  procedural-democracy framing, “we need a conversation”, etc.

Leninware Mode stays active unless explicitly disabled.
"""


def get_claude_output(youtube_url: str) -> dict:
    """Retrieve transcript → apply Leninware Mode → return JSON outputs."""

    logger.info(f"Fetching transcript (TranscriptAPI.com) for {youtube_url}")
    transcript = get_video_transcript(youtube_url)

    # Trim just in case
    transcript = transcript[:9000]

    user_content = f"""
Here is the YouTube transcript:

\"\"\"{transcript}\"\"\"

Apply full Leninware Mode and produce ONLY valid JSON with:
"title", "description", "tts_script"
"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            system=LENINWARE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}]
        )

        raw = response.content[0].text.strip()
        return json.loads(raw)

    except Exception as e:
        logger.error(f"Claude error: {e}")
        raise RuntimeError(f"Claude error: {e}")