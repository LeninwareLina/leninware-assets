import os
import json
import logging
import anthropic

logger = logging.getLogger(__name__)

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise RuntimeError("CLAUDE_API_KEY env var is missing")

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


def get_claude_outputs(youtube_url: str) -> dict:
    """
    Ask Claude to:
    - look at the YouTube URL
    - pull whatever it needs (transcript, meaning, context)
    - return tts_script, title, description as JSON
    """
    prompt = f"""
You are part of an automated video pipeline.

Input: a YouTube URL.
Your tasks:
1. Fetch or infer the video's content.
2. Generate a fast-paced TTS script for a 45–70 second YouTube Short.
3. Generate a YouTube title.
4. Generate a YouTube description.

Important:
- Reply ONLY in JSON.
- Keys must be exactly: "tts_script", "title", "description".
- Value types must be strings.

URL:
{youtube_url}
"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1200,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract text blocks
    text_chunks = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text_chunks.append(block.text)

    full_text = "".join(text_chunks).strip()

    # Parse JSON
    try:
        data = json.loads(full_text)
    except json.JSONDecodeError:
        logger.error("Claude did not return valid JSON: %s", full_text)
        raise

    # Validate keys
    for key in ("tts_script", "title", "description"):
        if key not in data or not isinstance(data[key], str):
            raise ValueError(f"Claude output missing or invalid key: {key}")

    return data