from pathlib import Path
from openai import OpenAI
from config import require_env

SAFETY_PROMPT_PATH = Path("prompts/script_safety_filter.txt")

def _load_safety_prompt() -> str:
    if SAFETY_PROMPT_PATH.exists():
        return SAFETY_PROMPT_PATH.read_text(encoding="utf-8")
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
    raw_script = (raw_script or "").strip()
    if not raw_script:
        return raw_script

    client = OpenAI(api_key=require_env("OPENAI_API_KEY"))
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
            {"role": "user", "content": user_content},
        ],
        max_tokens=1200,
        temperature=0.4,
    )

    return (resp.choices[0].message.content or "").strip()