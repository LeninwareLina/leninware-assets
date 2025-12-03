# storyboard_prompt_generator.py

from typing import List
from config import USE_MOCK_AI, require_env

# Only import OpenAI if NOT in mock mode
if not USE_MOCK_AI:
    from openai import OpenAI


SYSTEM_PROMPT = """
You are an AI storyboard artist creating symbolic illustrations for a political
commentary video.

Your job:
- Capture the tone: radical, anti-capitalist, critical of power, systemic analysis.
- Use metaphor, symbolism, and allegory.
- The images MUST NOT include:
    - real people or identifiable likenesses
    - copyrighted characters or logos
    - graphic or gory violence
    - sexual content
    - extremist symbols or hate imagery
- You MAY depict:
    - class struggle symbolically
    - exploitation symbolically
    - oppression as metaphors
    - protests as silhouettes or crowds
    - power imbalance using scale, shadows, architecture, animals, weather, etc.
- Favor abstract, cinematic, artful scenes.
- The goal is expressive political imagery that will not trigger OpenAI moderation.

Return a numbered list of prompts ONLY.
"""


def generate_storyboard_prompts(script_text: str, num_images: int = 8) -> List[str]:
    """Generate storyboard prompts for visual scenes."""

    if not script_text.strip():
        print("[storyboard] ERROR: Empty script passed in.")
        return []

    # ----------------------------------------------------
    # MOCK MODE — deterministic, no API usage
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print(f"[storyboard:mock] Generating {num_images} mock storyboard prompts.")
        return [
            f"Mock symbolic scene #{i+1}: abstract metaphorical artwork based on the script."
            for i in range(num_images)
        ]

    # ----------------------------------------------------
    # REAL MODE — OpenAI call
    # ----------------------------------------------------
    print("[storyboard] Calling OpenAI to generate storyboard prompts...")

    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    user_prompt = f"""
Create {num_images} symbolic storyboard image prompts based on the following
political commentary script.

Focus on:
- metaphors for power, exploitation, solidarity, liberation
- visual storytelling without depicting specific people
- scenes appropriate for public video content

Script:
-----
{script_text}
-----

Return ONLY a numbered list.
    """.strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=900,
            temperature=0.8,
        )
    except Exception as e:
        print(f"[storyboard] ERROR calling OpenAI: {e}")
        return []

    raw = (response.choices[0].message.content or "").strip()

    if not raw:
        print("[storyboard] ERROR: Empty storyboard response from OpenAI.")
        return []

    # ----------------------------------------------------
    # PARSE NUMBERED LIST
    # ----------------------------------------------------
    prompts = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        # Remove leading "1. text" or "1) text"
        if line[0].isdigit():
            if "." in line:
                line = line.split(".", 1)[1].strip()
            elif ")" in line:
                line = line.split(")", 1)[1].strip()

        if line:
            prompts.append(line)

    if len(prompts) < num_images:
        print(f"[storyboard] WARNING: Expected {num_images} prompts, got {len(prompts)}")

    return prompts[:num_images]