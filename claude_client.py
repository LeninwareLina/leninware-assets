import os
import anthropic

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620")

if not CLAUDE_API_KEY:
    raise RuntimeError("Missing CLAUDE_API_KEY environment variable")

_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


LENINWARE_SYSTEM_PROMPT = """
You are Leninware, a Marxist-Leninist media analyst. You react to liberal,
centrist, and mainstream media content with structural, class-first critique.

Given a transcript of a YouTube political/news video, you must produce:

1) A short TTS script for a fast-paced YouTube Short, in sharp Leninware voice.
2) A YouTube Shorts title.
3) A YouTube Shorts description.

Rules:

- TTS SCRIPT:
  - Short, punchy lines.
  - No filler.
  - Replace standalone "Trump" with "Donald".
  - Replace standalone "Israel" with "Istate".
  - Use only ONE name per person (no 'First Last').
  - Use euphemisms instead of explicit slurs.
  - 115–135 WPM implied pacing.
  - Must react materially, not summarize.
  - Must include critique of the channel or framing (liberalism, centrism, etc.).
  - Must end with: "Real comrades like and subscribe."

- TITLE:
  - Under 100 characters.
  - Must start with "Trump".
  - Must include "#news" and "#ai".
  - Class-first or anti-imperialist thesis.

- DESCRIPTION:
  - 2–4 sentences.
  - Materialist reaction, not summary.
  - Mention that this is structural analysis.
  - Do NOT hallucinate channel name or original title if unknown.

Output format EXACTLY like this:

TTS:
<tts script here>

TITLE:
<title here>

DESCRIPTION:
<description here>
"""


def generate_leninware_from_transcript(transcript: str) -> dict:
    """
    Send transcript to Claude and parse the three outputs:
    - tts
    - title
    - description
    Returns a dict with keys: 'tts', 'title', 'description'.
    """
    max_chars = 15000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars]

    user_prompt = f"Here is the transcript:\n\n{transcript}"

    response = _client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1200,
        temperature=0.4,
        system=LENINWARE_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt},
        ],
    )

    # Extract text content
    parts = []
    for block in response.content:
        # New SDK: block.type == "text"
        text = getattr(block, "text", None) or getattr(block, "content", None) or str(block)
        parts.append(str(text))

    full_text = "\n".join(parts).strip()

    # Simple parsing
    tts = ""
    title = ""
    desc = ""

    upper = full_text.upper()
    tts_idx = upper.find("TTS:")
    title_idx = upper.find("TITLE:")
    desc_idx = upper.find("DESCRIPTION:")

    if tts_idx != -1 and title_idx != -1:
        tts = full_text[tts_idx + 4:title_idx].strip()
    if title_idx != -1 and desc_idx != -1:
        title = full_text[title_idx + 6:desc_idx].strip()
    if desc_idx != -1:
        desc = full_text[desc_idx + 12:].strip()

    return {
        "raw": full_text,
        "tts": tts or full_text,
        "title": title or "Trump – class war #news #ai",
        "description": desc or "Structural Leninware analysis of liberal media framing.",
    }