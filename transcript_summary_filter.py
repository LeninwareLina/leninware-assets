# transcript_summary_filter.py

from typing import Optional
from config import USE_MOCK_AI, require_env

# Only import OpenAI if NOT in mock mode
if not USE_MOCK_AI:
    from openai import OpenAI


SYSTEM_PROMPT = """
You are a political summarizer for long-form video transcripts.

Your task:
- Read a full transcript of a news or commentary segment.
- Produce a concise, structured, hybrid summary:
    - Organized into sections with short headings.
    - Each section contains bullet points capturing key claims, arguments, and facts.
- Preserve contradictions, bias, and framing so downstream critique is possible.

Content guidelines:
- DO NOT sanitize politics. Preserve the ideological slant and power framing.
- DO NOT "balance" or neutralize the speaker's position.
- You MAY briefly note obvious bias or omissions if important to understanding.
- Focus on:
    - who is speaking and on whose behalf
    - what events or policies are being discussed
    - what causes or explanations are being offered
    - what is being left unsaid (if clear from context)
- Avoid fluffy language. Be concrete, material, and specific.

Output format:
- Use Markdown-style headings and bullets.
- Example:

  ## Topic 1: [short heading]

  - Bullet point 1
  - Bullet point 2

  ## Topic 2: [short heading]

  - Bullet point 1
  - Bullet point 2

- Do NOT include any preamble like "Here is the summary".
- Do NOT mention that you are an AI.
"""


def _safe_fallback_summary(transcript: str) -> str:
    """
    Fallback summary in case of errors.
    Returns a short, generic description using the first part of the transcript.
    """
    snippet = (transcript or "").strip()
    if len(snippet) > 400:
        snippet = snippet[:400] + "..."

    if not snippet:
        snippet = "[no transcript content available]"

    return (
        "## Summary (Fallback)\n\n"
        "- A transcript was provided but the automated summarizer failed.\n"
        "- Below is a brief snippet of the raw transcript for context:\n\n"
        f"> {snippet}\n"
    )


def summarize_transcript(transcript: str, max_chars: int = 12000) -> str:
    """
    Summarize a long transcript into a structured hybrid summary (sections + bullets).

    - In MOCK MODE: returns a deterministic mock summary.
    - In REAL MODE: uses OpenAI gpt-4o-mini with a hard character cap.
    """

    raw = (transcript or "").strip()
    print(f"[summary] Received transcript length: {len(raw)} chars")

    if not raw:
        print("[summary] ERROR: Empty transcript passed to summarizer.")
        return _safe_fallback_summary("")

    # ----------------------------------------------------
    # MOCK MODE — cheap, deterministic summary
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print("[summary:mock] Mock mode enabled — returning dummy structured summary.")
        return (
            "## Mock Topic 1: Media framing and narrative\n\n"
            "- This is a mock summary generated in mock mode.\n"
            "- The original transcript is not being processed by a real model.\n\n"
            "## Mock Topic 2: Power, class, and ideology\n\n"
            "- Assume the segment reflects mainstream institutional perspectives.\n"
            "- Leninware will use this as a stand-in to test downstream commentary.\n"
        )

    # ----------------------------------------------------
    # REAL MODE — use OpenAI gpt-4o-mini
    # ----------------------------------------------------
    print("[summary] REAL MODE — generating structured summary with gpt-4o-mini.")

    # Truncate transcript to avoid excessive token usage
    if len(raw) > max_chars:
        print(f"[summary] Transcript too long ({len(raw)} chars). Truncating to {max_chars} chars.")
        raw = raw[:max_chars]

    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    user_prompt = f"""
Summarize the following transcript into a structured, hybrid outline:
- Use 3–6 sections.
- Each section has a short heading.
- Each section has 2–5 bullet points summarizing key claims, arguments, and facts.
- Preserve the political framing and bias for later critique.

Transcript:
-----
{raw}
-----
    """.strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=900,
            temperature=0.5,
        )
    except Exception as e:
        print(f"[summary] ERROR calling OpenAI summarizer: {e}")
        return _safe_fallback_summary(transcript)

    content: Optional[str] = (response.choices[0].message.content or "").strip()

    if not content:
        print("[summary] ERROR: Empty summary returned from OpenAI.")
        return _safe_fallback_summary(transcript)

    print(f"[summary] Summary generated ({len(content)} chars).")
    return content