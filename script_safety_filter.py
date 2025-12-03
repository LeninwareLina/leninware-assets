# script_safety_filter.py

from pathlib import Path
from config import USE_MOCK_AI, require_env

# Only import OpenAI when NOT in mock mode
if not USE_MOCK_AI:
    from openai import OpenAI

SAFETY_PROMPT_PATH = Path("prompts/script_safety_filter.txt")


def _load_safety_prompt() -> str:
    if SAFETY_PROMPT_PATH.exists():
        return SAFETY_PROMPT_PATH.read_text(encoding="utf-8")

    # Default fallback rules
    return (
        "You are a safety post-processor for a political commentary script. "
        "Your job is to make the script compliant with platform safety rules "
        "without weakening its political analysis or tone. "
        "Do NOT remove radical critique, but:\n"
        "- Remove explicit calls for violence.\n"
        "- Remove doxxing or targeting private individuals.\n"
        "- Remove slurs and explicit hate speech.\n"
    )


def apply_script_safety_filter(raw_script: str) -> str:
    """Apply post-processing to keep the script compliant while preserving tone."""

    raw_script = (raw_script or "").strip()
    if not raw_script:
        return raw_script

    # ----------------------------------------------------
    # MOCK MODE → Do not rewrite anything
    # ----------------------------------------------------
    if USE_MOCK_AI:
        # In mock mode, return the script unchanged.
        # We do NOT censor political content in mock mode.
        return raw_script

    # ----------------------------------------------------
    # REAL MODE → Call OpenAI to refine the script safely
    # ----------------------------------------------------
    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    system_prompt = _load_safety_prompt()

    user_content = (
        "Here is a commentary script. Return a single revised version that "
        "preserves the political content and style, but complies with the safety rules.\n\n"
        "<<<BEGIN_SCRIPT>>>\n"
        f"{raw_script}\n"
        "<<<END_SCRIPT>>>"
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",  "content": user_content},
        ],
        max_tokens=1200,
        temperature=0.4,
    )

    return (resp.choices[0].message.content or "").strip()