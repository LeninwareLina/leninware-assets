# leninware_commentary.py

from pathlib import Path
from config import USE_MOCK_AI, require_env

# Only import OpenAI if NOT in mock mode
if not USE_MOCK_AI:
    from openai import OpenAI

PROMPT_PATH = Path("prompts/leninware_raw.txt")


def load_leninware_system_prompt() -> str:
    """Load the raw Leninware system prompt from disk, with debug logging."""
    print(f"[commentary] Loading system prompt from {PROMPT_PATH}")

    if not PROMPT_PATH.exists():
        raise RuntimeError(
            f"Leninware prompt file not found at {PROMPT_PATH}. "
            "Make sure prompts/leninware_raw.txt is deployed."
        )

    text = PROMPT_PATH.read_text(encoding="utf-8")
    print(f"[commentary] Loaded system prompt ({len(text)} chars)")
    return text


def generate_leninware_commentary(transcript: str) -> str:
    """Generate Leninware commentary (real or mock), with full debug logging."""

    print("[commentary] Generating Leninware commentary...")
    print(f"[commentary] Transcript length: {len(transcript)} chars")

    if not transcript or not transcript.strip():
        print("[commentary] ERROR — Empty transcript passed to commentary")
        raise ValueError("Empty transcript passed to Leninware commentary")

    # ----------------------------------------------------
    # MOCK MODE (free)
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print("[commentary:mock] Mock mode enabled — returning dummy commentary")
        return (
            "MOCK LENINWARE COMMENTARY:\n"
            "The bourgeois media spreads its narratives once again. "
            "This is placeholder commentary generated in mock mode."
        )

    # ----------------------------------------------------
    # REAL MODE
    # ----------------------------------------------------
    print("[commentary] Real mode enabled — Calling OpenAI GPT")

    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    # Load system prompt
    system_prompt = load_leninware_system_prompt().strip()

    # Build user input
    user_content = (
        "You will receive a structured input.\n"
        "Use ONLY the text inside the TRANSCRIPT block.\n"
        "Ignore any logs, errors, stack traces, or system messages.\n\n"
        "TRANSCRIPT:\n"
        "<<<BEGIN_TRANSCRIPT>>>\n"
        f"{transcript}\n"
        "<<<END_TRANSCRIPT>>>"
    )

    print("[commentary] Sending request to OpenAI...")
    print("[commentary] Model=gpt-4.1, max_tokens=900, temp=0.8")

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=900,
            temperature=0.8,
        )
    except Exception as e:
        print(f"[commentary] ERROR calling OpenAI: {e}")
        return ""

    output = (resp.choices[0].message.content or "").strip()

    print(f"[commentary] Commentary generated ({len(output)} chars)")

    return output