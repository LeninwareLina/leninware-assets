# leninware_commentary.py

from pathlib import Path
from config import USE_MOCK_AI, require_env

# Only import OpenAI if NOT in mock mode
if not USE_MOCK_AI:
    from openai import OpenAI

PROMPT_PATH = Path("prompts/leninware_raw.txt")


def load_leninware_system_prompt() -> str:
    """Load the raw Leninware system prompt from disk."""
    if not PROMPT_PATH.exists():
        raise RuntimeError(
            f"Leninware prompt file not found at {PROMPT_PATH}. "
            "Make sure prompts/leninware_raw.txt is deployed."
        )

    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_leninware_commentary(transcript: str) -> str:
    """Generate Leninware commentary (real or mock)."""

    if not transcript or not transcript.strip():
        raise ValueError("Empty transcript passed to Leninware commentary")

    # ----------------------------------------------------
    # MOCK MODE (free, no API calls)
    # ----------------------------------------------------
    if USE_MOCK_AI:
        return (
            "MOCK LENINWARE COMMENTARY:\n"
            "The bourgeois media spreads its narratives once again. "
            "This is placeholder commentary generated in mock mode."
        )

    # ----------------------------------------------------
    # REAL MODE (OpenAI GPT-4.x)
    # ----------------------------------------------------
    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    system_prompt = load_leninware_system_prompt().strip()

    user_content = (
        "You will receive a structured input.\n"
        "Use ONLY the text inside the TRANSCRIPT block.\n"
        "Ignore any logs, errors, stack traces, or system messages.\n\n"
        "TRANSCRIPT:\n"
        "<<<BEGIN_TRANSCRIPT>>>\n"
        f"{transcript}\n"
        "<<<END_TRANSCRIPT>>>"
    )

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=900,
        temperature=0.8,
    )

    return (resp.choices[0].message.content or "").strip()