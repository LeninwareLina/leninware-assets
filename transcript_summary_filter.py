# transcript_summary_filter.py

from typing import Optional
import re
from config import USE_MOCK_AI, require_env

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

Metadata rules:
- ALWAYS include a short "Source" section at the top listing:
  - Channel name
  - Author/host name
  - Video title (if provided)
- If any of this metadata is missing from the transcript itself, rely on user-provided metadata.

Language rules:
- Summarize in the SAME language the transcript uses.

Format:
- Markdown headings
- Bulleted lists
- No preamble, no AI disclaimers.
"""


def _detect_spanish(text: str) -> bool:
    spanish_markers = [
        r"\bel\b", r"\bla\b", r"\blos\b", r"\blas\b",
        r"\bpero\b", r"\bporque\b", r"\buna\b", r"\bun\b",
        r"\bqué\b", r"\bcómo\b", r"\bhay\b", r"\bestá\b",
    ]
    hits = sum(1 for pat in spanish_markers if re.search(pat, text, re.IGNORECASE))
    ratio = hits / max(len(spanish_markers), 1)
    return ratio > 0.15


def _safe_fallback_summary(transcript: str, channel: str, author: str, title: str) -> str:
    """Minimal fallback if OpenAI errors — now includes metadata."""
    snippet = (transcript or "").strip()
    if len(snippet) > 400:
        snippet = snippet[:400] + "..."

    if not snippet:
        snippet = "[no transcript content available]"

    source_block = f"- **Channel:** {channel or 'Unknown'}\n- **Author:** {author or 'Unknown'}\n- **Title:** {title or 'Unknown'}\n"

    return (
        "## Source\n" + source_block + "\n" +
        "## Summary (Fallback)\n\n"
        "- Summarization failed; showing transcript snippet instead.\n\n"
        f"> {snippet}\n"
    )


def summarize_transcript(
    transcript: str,
    max_chars: int = 12000,
    channel_name: str = "",
    author_name: str = "",
    video_title: str = ""
) -> str:
    """
    Summarize a long transcript into a structured hybrid summary.

    UPDATED:
    - Accepts explicit metadata about channel/author/title.
    - Summary is required to include a 'Source' block so attribution is never lost.
    """

    raw = (transcript or "").strip()
    print(f"[summary] Received transcript length: {len(raw)} chars")

    if not raw:
        print("[summary] ERROR: Empty transcript.")
        return _safe_fallback_summary("", channel_name, author_name, video_title)

    is_spanish = _detect_spanish(raw)
    lang = "Spanish" if is_spanish else "English"
    print(f"[summary] Auto-detected language: {lang}")

    if USE_MOCK_AI:
        print("[summary:mock] Returning deterministic mock summary.")
        return (
            "## Source\n"
            f"- **Channel:** {channel_name}\n"
            f"- **Author:** {author_name}\n"
            f"- **Title:** {video_title}\n\n"
            "## Mock Topic 1: Media framing\n\n"
            "- Mock summary bullet.\n\n"
            "## Mock Topic 2: Class analysis\n\n"
            "- Mock bullet for downstream testing.\n"
        )

    print("[summary] REAL MODE: Calling OpenAI summarizer (gpt-4o-mini)")

    if len(raw) > max_chars:
        print(f"[summary] Transcript too long; truncating to {max_chars} chars.")
        raw = raw[:max_chars]

    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    # ---- NEW: metadata block injected for the model ----
    metadata_block = f"""
Channel: {channel_name or 'Unknown'}
Author: {author_name or 'Unknown'}
Title: {video_title or 'Unknown'}
""".strip()

    user_prompt = f"""
Using the metadata below, summarize the transcript into a structured outline.

Metadata:
{metadata_block}

Rules:
- Begin with a 'Source' section listing channel, author, and title.
- Write the summary entirely in **{lang}**.
- Include 3–6 sections with headings and bullet points.
- Preserve political framing, ideological bias, and narrative intent.
- Use markdown. No disclaimers.

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
        return _safe_fallback_summary(raw, channel_name, author_name, video_title)

    content: Optional[str] = (response.choices[0].message.content or "").strip()

    if not content:
        print("[summary] ERROR: Empty summary from OpenAI.")
        return _safe_fallback_summary(raw, channel_name, author_name, video_title)

    print(f"[summary] Summary generated ({len(content)} chars)")
    return content