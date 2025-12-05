# script_safety_filter.py

from pathlib import Path
from config import USE_MOCK_AI, require_env, LENINWARE_LANG_MODE

# Only import OpenAI when NOT in mock mode
if not USE_MOCK_AI:
    from openai import OpenAI

SAFETY_PROMPT_PATH_EN = Path("prompts/script_safety_filter_en.txt")
SAFETY_PROMPT_PATH_ES = Path("prompts/script_safety_filter_es.txt")


def _load_safety_prompt(lang: str) -> str:
    """Load language-specific safety rules with debug logging."""

    if lang == "es":
        path = SAFETY_PROMPT_PATH_ES
    else:
        path = SAFETY_PROMPT_PATH_EN

    if path.exists():
        print(f"[safety_filter] Loading {lang.upper()} safety rules from {path}")
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            print(f"[safety_filter] WARNING: {path} is empty!")
        return text

    print(f"[safety_filter] WARNING: No {lang.upper()} safety rules found. Using built-in defaults.")

    if lang == "es":
        return (
            "Eres un post-procesador de seguridad para un guion político.\n"
            "Tu tarea es que el texto cumpla normas de seguridad sin suavizar "
            "el análisis crítico ni la postura ideológica. NO elimines crítica radical, pero:\n"
            "- Elimina llamados explícitos a la violencia.\n"
            "- Elimina doxxing o identificación de personas privadas.\n"
            "- Elimina insultos o discurso de odio explícito.\n"
        )

    # fallback EN
    return (
        "You are a safety post-processor for a political commentary script. "
        "Your job is to make the script compliant with platform safety rules "
        "without weakening its political analysis or tone. Do NOT remove radical critique, but:\n"
        "- Remove explicit calls for violence.\n"
        "- Remove doxxing or targeting private individuals.\n"
        "- Remove slurs and explicit hate speech.\n"
    )


def _detect_language(text: str) -> str:
    """Cheap heuristic to detect Spanish vs English."""
    text = text.lower()

    spanish_markers = ["que ", " de ", " la ", " el ", " y ", " para ", " como ",
                       "pero", "porque", "cuando", "según", "gobierno", "política"]

    matches = sum(1 for w in spanish_markers if w in text)

    if matches >= 3:
        return "es"
    return "en"


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
    # Detect language (ES vs EN)
    # ----------------------------------------------------
    lang = LENINWARE_LANG_MODE or _detect_language(raw_script)
    print(f"[safety_filter] Detected language: {lang.upper()}")

    # ----------------------------------------------------
    # REAL MODE — CALL OPENAI
    # ----------------------------------------------------
    print("[safety_filter] REAL MODE — Applying OpenAI safety filter...")

    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    system_prompt = _load_safety_prompt(lang)

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