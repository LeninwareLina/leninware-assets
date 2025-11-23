# leninware_commentary.py

from pathlib import Path
from openai import OpenAI

from config import OPENAI_API_KEY, require_env

PROMPT_PATH = Path("prompts/leninware_raw.txt")


def load_leninware_system_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise RuntimeError(
            f"Leninware prompt file not found at {PROMPT_PATH}. "
            "Create it and paste your system prompt there."
        )
    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_leninware_commentary(transcript: str) -> str:
    """
    Sends transcript to GPT-4.1 using your Leninware system prompt.

    Returns: commentary string (whatever 4.1 outputs).
    """
    require_env("OPENAI_API_KEY", OPENAI_API_KEY)
    client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = load_leninware_system_prompt().strip()

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "Here is the transcript from a YouTube video.\n\n"
                    "Apply the Leninware rules you were given and produce your commentary.\n\n"
                    "TRANSCRIPT:\n"
                    f"{transcript}"
                ),
            },
        ],
        max_tokens=900,
        temperature=0.8,
    )

    return resp.choices[0].message.content.strip()