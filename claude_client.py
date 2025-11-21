import os
import json
from typing import Dict, Any

from anthropic import Anthropic, APIError

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")


class ClaudeError(Exception):
    """Raised when Claude generation fails."""


def _get_client() -> Anthropic:
    if not CLAUDE_API_KEY:
        raise ClaudeError("CLAUDE_API_KEY environment variable is not set.")
    return Anthropic(api_key=CLAUDE_API_KEY)


SYSTEM_PROMPT = """
You are Leninware, a militant Marxist-Leninist analysis engine.

You receive:
- A full YouTube transcript in Markdown (from TranscriptAPI, including title/metadata).
- Your job is to produce three things ONLY: a short title, a punchy description, and a TTS-ready monologue.

Rules:
- Be clearly socialist, anti-fascist, anti-capitalist, and anti-racist.
- Critique reactionary, liberal, or fascist positions directly.
- Do NOT ramble; be sharp, structured, and concrete.
- The TTS script must be written as if Leninware is speaking directly to the listener.

IMPORTANT OUTPUT FORMAT:
Return a SINGLE JSON object with exactly these keys:
{
  "title": "short YouTube title string",
  "description": "short but vivid YouTube description",
  "tts_script": "full monologue for text-to-speech"
}

Do NOT wrap the JSON in backticks or any other text. No explanations, only raw JSON.
""".strip()


def _extract_json_block(text: str) -> str:
    """
    Claude sometimes wraps JSON in extra commentary.
    This extracts the first {...} block.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ClaudeError("Claude did not return valid JSON.")
    return text[start : end + 1]


def generate_leninware_outputs(transcript_markdown: str) -> Dict[str, Any]:
    """
    Call Claude to generate Leninware title, description, and TTS script.

    Returns a dict with keys: title, description, tts_script.
    """
    client = _get_client()

    user_content = (
        "Here is a YouTube transcript in Markdown format, including metadata.\n\n"
        "Use it to generate the Leninware outputs as specified in the system prompt.\n\n"
        "=== TRANSCRIPT START ===\n"
        f"{transcript_markdown}\n"
        "=== TRANSCRIPT END ==="
    )

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.4,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
    except APIError as e:
        raise ClaudeError(f"Claude API error: {e}") from e
    except Exception as e:
        raise ClaudeError(f"Unexpected Claude error: {e}") from e

    # anthropic python client: response.content is a list of content blocks
    if not response.content:
        raise ClaudeError("Claude returned empty content.")

    text = ""
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text += block.text

    if not text:
        raise ClaudeError("Claude returned no text content.")

    try:
        json_str = _extract_json_block(text)
        data = json.loads(json_str)
    except Exception as e:
        raise ClaudeError(f"Failed to parse Claude JSON: {e}") from e

    # Basic sanity defaults
    return {
        "title": data.get("title", "Leninware Analysis"),
        "description": data.get("description", "No description provided."),
        "tts_script": data.get("tts_script", ""),
    }