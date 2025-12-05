# transcript_summary_filter.py

from typing import Optional
import re
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

Language rules:
- Summarize in the SAME language the transcript uses.
- If the transcript is Spanish, summarize entirely in Spanish.
- If English, summarize in English.
- If mixed, choose the dominant language.

Content guidelines:
- DO NOT sanitize politics.
- Do NOT "balance" the ideological slant.
- You MAY note bias or omissions if needed.
- Focus on: narrative framing, power relations, causes, impacts.

Format:
- Markdown headings
- Bulleted lists
- No preamble, no AI disclaimers.
"""


def _detect_spanish(text: str) -> bool:
    """
    Very lightweight language heuristic.
    We check for common Spanish functional words.
    """
    spanish_markers = [
        r"\bel\b", r"\bla\b", r"\blos\b", r"\blas\b",
        r"\bpero\b", r"\bporque\b", r"\buna\b", r"\bun\b",
        r"\bqué\b", r"\bcómo\b", r"\bhay\b", r"\bestá\b",
    ]

    hits = sum(1 for pat in spanish_markers if re.search(pat, text, re.IGNORECASE))
    ratio = hits / max(len(spanish_markers), 1)

    return ratio > 0.15  # ~15% hits = probably Spanish


def _safe_fallback_summary(transcript: str) -> str:
    """Minimal fallback if OpenAI errors."""
    snippet = (transcript or "").strip()
    if len(snippet) > 400:
        snippet = snippet[:400] + "..."

    if not snippet:
        snippet = "[no transcript content available]"

    return (
        "## Summary (Fallback)\n\n"
        "- A transcript was provided but summarization failed.\n"
        "- Below is a short snippet:\n\n"
        f"> {snippet}\n"
    )


def summarize_transcript(transcript: str, max_chars: int = 12000) -> str:
    """
    Summarize a long transcript into a structured hybrid summary.

    NEW: Automatically preserves the language of the source transcript.
    """

    raw = (transcript or "").strip()
    print(f"[summary] Received transcript length: {len(raw)} chars")

    if not raw:
        print("[summary] ERROR: Empty transcript.")
        return _safe_fallback_summary("")

    # -----------------------------------------------
    # Detect language automatically
    # -----------------------------------------------
    is_spanish = _detect_spanish(raw)
    lang = "Spanish" if is_spanish else "English"
    print(f"[summary] Auto-detected language: {lang}")

    # -----------------------------------------------
    # MOCK MODE
    # -----------------------------------------------
    if USE_MOCK_AI:
        print("[summary:mock] Returning deterministic mock summary.")
        return (
            "## Mock Topic 1: Media framing\n\n"
            "- Mock summary bullet.\n\n"
            "## Mock Topic 2: Class analysis\n\n"
            "- Mock bullet for downstream testing.\n"
        )

    # -----------------------------------------------
    # REAL MODE — gpt-4o-mini
    # -----------------------------------------------
    print("[summary] REAL MODE: Calling OpenAI summarizer (gpt-4o-mini)")

    # Trim excessively long transcripts to control cost
    if len(raw) > max_chars:
        print(f"[summary] Transcript too long; truncating to {max_chars} chars.")
        raw = raw[:max_chars]

    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    user_prompt = f"""
Summarize the following transcript into a structured outline.
- Write the summary entirely in **{lang}**.
- Use 3–6 sections.
- Each section must have:
  - a short heading
  - 2–5 bullet points
- Preserve political framing, ideological bias, and narrative intentions.
- No preambles, no disclaimers.

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
        print(f"[summary] ERROR calling OpenAI: {e}")
        return _safe_fallback_summary(transcript)

    content: Optional[str] = (response.choices[0].message.content or "").strip()

    if not content:
        print("[summary] ERROR: Empty summary from OpenAI.")
        return _safe_fallback_summary(transcript)

    print(f"[summary] Summary generated ({len(content)} chars)")
    return content