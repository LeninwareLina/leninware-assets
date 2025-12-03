# script_safety_filter.py

from pathlib import Path
from config import USE_MOCK_AI, require_env

# Only import OpenAI when NOT in mock mode
if not USE_MOCK_AI:
    from openai import OpenAI

SAFETY_PROMPT_PATH = Path("prompts/script_safety_filter.txt")


def _load_safety_prompt() -> str:
    """Load safety rules with debug logging."""
    if SAFETY_PROMPT_PATH.exists():
        print(f"[safety_filter] Loading safety rules from {SAFETY_PROMPT_PATH}")
        text = SAFETY_PROMPT_PATH.read_text(encoding="utf-8").strip()
        if not text:
            print("[safety_filter] WARNING: Safety prompt file is empty!")
        return text

    print("[safety_filter] WARNING: No custom safety rules found. Using built-in defaults.")

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

    print(f"[safety_filter] Received script length: {len(raw_script)} chars")

    if not raw_script:
        print("[safety_filter] EMPTY SCRIPT — Skipping safety filter.")
        return raw_script

    # ----------------------------------------------------
    # MOCK MODE
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print("[safety_filter] MOCK MODE — Returning script unchanged.")
        return raw_script

    # ----------------------------------------------------
    # REAL MODE
    # ----------------------------------------------------
    print("[safety_filter] REAL MODE — Applying OpenAI safety filter...")

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

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",  "content": user_content},
            ],
            max_tokens=1200,
            temperature=0.4,
        )

        safe = (resp.choices[0].message.content or "").strip()

        print(
            f"[safety_filter] Finished. "
            f"Output length: {len(safe)} chars "
            f"(delta: {len(safe) - len(raw_script)})"
        )

        return safe

    except Exception as e:
        print("[safety_filter] ERROR calling OpenAI safety filter:", e)
        print("[safety_filter] FALLBACK — Returning raw script unchanged.")
        return raw_script