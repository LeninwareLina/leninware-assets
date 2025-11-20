import os
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Load Claude API key from Railway
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise RuntimeError("CLAUDE_API_KEY env var is missing")

# Initialize Claude client
client = Anthropic(api_key=CLAUDE_API_KEY)


def get_claude_output(youtube_url: str) -> dict:
    """
    Sends the YouTube URL to Claude and returns:
      - title
      - description
      - tts_script
    """

    logger.info("Calling Claude for YT analysis...")

    prompt = f"""
You are Leninware, an automated pipeline tool.

The user will send ONLY a YouTube URL.
You MUST:

1. Retrieve the transcript (use your internal tools).
2. Summarize the content into:
   - A short, punchy YouTube TITLE.
   - A brief YouTube DESCRIPTION (1–2 sentences).
3. Generate a strong, clear, high-energy, female-voiced TTS SCRIPT suitable for a 1-minute YouTube Short.
4. End the TTS script with the line:
   "Real comrades like and subscribe."

Return your output in **valid JSON only**, with EXACTLY these fields:

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
            model="claude-3-5-sonnet-latest",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Claude returns a list of content blocks. We want the text of the first one.
        raw_text = response.content[0].text.strip()

        import json
        data = json.loads(raw_text)

        logger.info("Claude returned valid JSON.")
        return data

    except Exception as e:
        logger.error(f"Claude error: {e}")
        raise RuntimeError(f"Claude error: {e}")