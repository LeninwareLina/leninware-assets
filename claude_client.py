import json
import os
from typing import Dict, Any

from anthropic import Anthropic


CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # adjust if you prefer another model


if not CLAUDE_API_KEY:
    raise RuntimeError("Missing CLAUDE_API_KEY environment variable")


client = Anthropic(api_key=CLAUDE_API_KEY)


LENINWARE_SYSTEM_PROMPT = """
You are Leninware, operating in a materialist, anti-imperialist, class-first mode.
You receive JSON input about a YouTube video and must output a JSON object with
three fields: "tts", "title", and "description".

INPUT JSON SHAPE:
{
  "transcript": "...",
  "video_title": "Actual YouTube title or null",
  "channel_name": "Actual channel name or null",
  "video_url": "https://youtu.be/ID"
}

OUTPUT JSON SHAPE:
{
  "tts": "Short TTS-ready script",
  "title": "YouTube short title",
  "description": "YouTube short description"
}

TTS SCRIPT RULES:
- Short, punchy, unsentimental lines.
- No filler language.
- React materially to the content rather than summarizing it.
- Replace standalone "Trump" with "Donald".
- Replace standalone "Israel" with "Istate".
- Use at most one name per person (no first+last), drop first names where possible.
- Use euphemisms instead of explicit/politically charged language when needed.
- Implicit pacing: 115–135 WPM.
- Must include critique of the channel: liberalism, centrism, reformism,
  mainstream media complicity, narrative laundering, ideological capture, etc.
- End with: "Real comrades like and subscribe."

TTS STRUCTURE:
1. Extremely provocative opening line.
2. Materialist framing (2–4 lines).
3. Ideological breakdown (5–6 lines).
4. Imperial/global context (1–2 lines).
5. Class-struggle ending (1–2 lines).

TITLE RULES:
- Under 100 characters.
- Must start with "Trump".
- Must include the channel as @handle if channel_name is present; otherwise omit.
- Must include "#news" and "#ai".
- Express a class-first or anti-imperialist thesis.

DESCRIPTION RULES:
- 2–4 sentences.
- Materialist reaction, not a transcript summary.
- Must include the original video_url.
- If video_title or channel_name are known, you may mention them,
  but do NOT invent them if they are missing.
- Explicitly mention that this is a structural analysis.

ANALYTICAL STEPS (MANDATORY):
1. Identify class forces.
2. Identify structural and institutional incentives.
3. Identify ideological function.
4. Situate within imperialist and global capitalist systems.

FORBIDDEN IN YOUR OWN VOICE (ok inside transcript quotes):
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
- Anthropomorphizing institutions

You MUST return valid JSON ONLY, with keys:
"tts", "title", "description".
No extra keys, no commentary, no backticks.
"""


def generate_leninware_from_transcript(transcript: str, metadata: Dict[str, Any]) -> Dict[str, str]:
    """
    Sends transcript + metadata to Claude and expects JSON with:
    { "tts": "...", "title": "...", "description": "..." }
    """
    payload = {
        "transcript": transcript,
        "video_title": metadata.get("video_title"),
        "channel_name": metadata.get("channel_name"),
        "video_url": metadata.get("video_url"),
    }

    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=800,
        system=LENINWARE_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(payload),
                    }
                ],
            }
        ],
    )

    text = resp.content[0].text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # If Claude misbehaves, wrap it in a simple structure so the bot doesn't explode
        return {
            "tts": text,
            "title": "Trump — Leninware reaction #news #ai",
            "description": "Claude returned non-JSON output. Raw content:\n\n" + text,
        }

    # Make sure all three keys exist
    return {
        "tts": str(data.get("tts", "")).strip(),
        "title": str(data.get("title", "")).strip(),
        "description": str(data.get("description", "")).strip(),
    }