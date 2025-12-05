# leninware_commentary.py

from pathlib import Path
from config import USE_MOCK_AI, LANGUAGE_MODE, require_env

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


def _wrap_prompt_for_language(system_prompt: str) -> str:
    """
    Wrap the Leninware system prompt for bilingual mode.
    - LANGUAGE_MODE=en → return unchanged
    - LANGUAGE_MODE=es → wrap to enforce Rioplatense Spanish output
    """
    if LANGUAGE_MODE == "es":
        print("[commentary] LANGUAGE_MODE=es — Spanish commentary enabled.")
        return (
            "Responde SIEMPRE en español rioplatense natural, fluido y militante.\n"
            "No traduzcas literalmente; escribe como un comunicador político argentino.\n"
            "Mantén el tono marxista-leninista, antiimperialista y antiburgués.\n"
            "Evita modismos de España (no uses 'vale', 'vosotros', etc.) — usa 'vos', "
            "'laburo', 'quilombo', etc. cuando corresponda.\n\n"
            "A continuación sigue el prompt original de Leninware:\n\n"
            f"{system_prompt}"
        )
    else:
        print("[commentary] LANGUAGE_MODE=en — English commentary mode.")
        return system_prompt


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
    # REAL MODE — now uses gpt-4o-mini (cheap + stable)
    # ----------------------------------------------------
    print("[commentary] Real mode enabled — Calling OpenAI GPT")

    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    # Load original system prompt
    base_prompt = load_leninware_system_prompt().strip()

    # Wrap for bilingual mode
    system_prompt = _wrap_prompt_for_language(base_prompt)

    # Build user input
    user_content = (
        "Use ONLY the text inside the TRANSCRIPT block.\n"
        "Ignore logs, stack traces, or errors from any pipeline stage.\n\n"
        "TRANSCRIPT:\n"
        "<<<BEGIN_TRANSCRIPT>>>\n"
        f"{transcript}\n"
        "<<<END_TRANSCRIPT>>>"
    )

    print("[commentary] Sending request to OpenAI...")
    print("[commentary] Model=gpt-4o-mini, max_tokens=900, temp=0.8")

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
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