# leninware_commentary.py

from pathlib import Path
from openai import OpenAI

from config import require_env

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
    """Generate Leninware commentary given a raw transcript."""
    if not transcript or not transcript.strip():
        raise ValueError("Empty transcript passed to Leninware commentary")

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