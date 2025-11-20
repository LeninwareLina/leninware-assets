import os
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Load Claude API Key from Railway
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise RuntimeError("CLAUDE_API_KEY env var is missing")

# Initialize Anthropic client
client = Anthropic(api_key=CLAUDE_API_KEY)


def get_claude_output(youtube_url: str) -> dict:
    """
    Sends a YouTube URL to Claude (Haiku model) and returns:
      - title
      - description
      - tts_script
    All in JSON format.
    """

    logger.info("Calling Claude (Haiku)…")

    prompt = f"""
You are Leninware.

The user will only give you a YouTube URL.
You MUST:

1. Retrieve the YouTube transcript using your internal tools.
2. Create:
   - a punchy YouTube TITLE
   - a brief DESCRIPTION (1–2 sentences)
   - a TTS SCRIPT for a ~1 minute YouTube Short
3. End the TTS script with the line:
   "Real comrades like and subscribe."

Return ONLY VALID JSON in this exact shape:

{{
  "title": "...",
  "description": "...",
  "tts_script": "..."
}}

Now process this video:
{youtube_url}
"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-latest",    # <-- works for all API accounts
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract text content (Haiku returns a content list)
        raw_text = response.content[0].text.strip()

        import json
        data = json.loads(raw_text)

        logger.info("Claude returned valid JSON.")
        return data

    except Exception as e:
        logger.error(f"Claude error: {e}")
        raise RuntimeError(f"Claude error: {e}")