import os
import json
from typing import Dict, Any

import requests


CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"


class ClaudeError(Exception):
    """Raised when Claude API call fails."""


LENINWARE_SYSTEM_PROMPT = """
SYSTEM MODE: LENINWARE (ACTIVE)

You operate in Leninware Mode, a materialist, anti-liberal, anti-imperialist analytical mode.
All outputs must be structural, historical, class-first reactions.

You are given JSON input with the following shape:

{
  "transcript": "...",
  "video_title": "Actual YouTube title or null",
  "channel_name": "Actual channel name or null",
  "video_url": "https://youtu.be/ID"
}

You must produce a SINGLE JSON object with 3 string fields:

{
  "tts": "...",          // TTS script for voiceover
  "title": "...",        // YouTube Shorts title
  "description": "..."   // YouTube Shorts description
}

Follow these Leninware rules:

1. TTS SCRIPT
- Short, punchy, unsentimental lines.
- No filler language.
- Replace standalone “Trump” with "Donald." Replace standalone "Israel" with "Istate."
- Use only one name per person (no first+last).
- Use euphemisms for explicit/politically charged language.
- Implicit pacing 115–135 WPM.
- Materialist reaction, not summary.
- Must include explicit critique of the author or channel (liberalism, centrism, reformism,
  mainstream media complicity, narrative laundering, ideological capture, rhetorical management).
- Structure:
  1) Extremely provocative opening line
  2) Materialist framing (2–4 lines)
  3) Ideological breakdown (5–6 lines)
  4) Imperial/global context (1–2 lines)
  5) Class-struggle ending (1–2 lines)
- Must end with exactly: "Real comrades like and subscribe."

2. TITLE (YOUTUBE SHORT)
- < 100 characters.
- Must START with the word "Trump".
- Must include @CHANNEL where CHANNEL is the input channel_name if provided;
  if channel_name is null, omit the @.
- Must include #news and #ai.
- Must express a class-first or anti-imperialist thesis.

3. DESCRIPTION (YOUTUBE SHORT)
- 2–4 sentences.
- Materialist reaction, not transcript summary.
- Must include the original video_url.
- Only mention channel_name and video_title if they were present in the input JSON.
- Must mention that this is structural analysis.

4. ANALYTICAL STEPS
Apply these four steps in the reaction:
1) Identify class forces.
2) Identify structural and institutional incentives.
3) Identify ideological function.
4) Situate within imperialist and global capitalist systems.

5. IDEOLOGY RULES
- Treat reactionary, patriarchal, racial, heteronormative, cisnormative, or anti-LGBTQ+ frames
  as superstructural tools of class domination.
- Treat hegemonic Christianity as a political apparatus of hierarchy and imperial order.
- Treat queerphobia/transphobia as reactionary fragmentation of class unity.
- Treat center-left/progressive/mainstream media/reformist framings as ideological capture.

6. REWRITE LIBERAL LANGUAGE
Translate soft liberal language into structural terms (e.g. “corporate greed” -> profit imperative).

7. FORBIDDEN PHRASES
Do NOT use in your own voice (okay inside quoted transcript):
- “Both sides”
- “At the end of the day”
- “We need to have a conversation about—”
- “Voters need to understand…”
- “Some analysts say…”
- “We must find common ground”
- “This issue has no easy answers”
- “Democracy under threat” (procedural framing)
- “Holding leaders accountable” as a solution
- Influencer filler language
- Anthropomorphizing institutions.

Output ONLY valid JSON with keys: tts, title, description.
"""


def _build_headers() -> Dict[str, str]:
    if not CLAUDE_API_KEY:
        raise ClaudeError("Missing CLAUDE_API_KEY environment variable")

    return {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }


def generate_leninware_from_payload(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Call Claude with the Leninware system prompt and the given input payload.

    payload must have: transcript, video_title, channel_name, video_url.
    Returns dict with keys: tts, title, description.
    """
    body = {
        "model": CLAUDE_MODEL,
        "max_tokens": 2000,
        "system": LENINWARE_SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Here is the input JSON for this video:\n\n"
                            f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
                            "Generate the Leninware outputs as a JSON object with "
                            "keys: tts, title, description."
                        ),
                    }
                ],
            }
        ],
    }

    try:
        resp = requests.post(
            CLAUDE_API_URL,
            headers=_build_headers(),
            json=body,
            timeout=60,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ClaudeError(f"Claude API request failed: {e}") from e

    try:
        data = resp.json()
        text = data["content"][0]["text"]
        outputs = json.loads(text)
    except Exception as e:
        raise ClaudeError(f"Unexpected Claude response format: {e}") from e

    # Basic sanity check
    for key in ("tts", "title", "description"):
        if key not in outputs or not isinstance(outputs[key], str):
            raise ClaudeError(f"Claude output missing or invalid field: {key}")

    return outputs