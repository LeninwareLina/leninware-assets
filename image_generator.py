# image_generator.py
"""
Generate Leninware-style surreal political collage images
from a TTS script using OpenAI's image API.

Style: Surreal, high-contrast political propaganda collage
(Option B you chose).
"""

import os
from typing import List
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

client = OpenAI(api_key=OPENAI_API_KEY)


def _build_base_prompt(tts_script: str) -> str:
    """
    Build a base style prompt for Leninware visuals based on the TTS script.
    We don’t try to summarize everything, just steer the vibe.
    """
    return (
        "Surreal political propaganda collage, dramatic lighting, "
        "high contrast, focused on class struggle, capitalism, media, "
        "and imperialism. No faces of real people, no realistic politicians. "
        "Use symbols: money, chains, towers, microphones, news screens, "
        "riot police silhouettes, crowds, flags, and abstract power imagery. "
        "Cinematic, sharp, vertical 9:16 framing. "
        "Inspired by the following radical commentary text (do not render text): "
        f"{tts_script[:600]}"
    )


def generate_leninware_images(tts_script: str, n_images: int = 3) -> List[str]:
    """
    Generate n_images surreal Leninware-style collage images
    and return a list of HTTPS URLs.

    Each call costs a bit of OpenAI image credit, so keep n_images modest.
    """
    if n_images < 1:
        n_images = 1
    if n_images > 4:
        n_images = 4  # cap for safety

    prompt = _build_base_prompt(tts_script)

    response = client.images.generate(
        model="gpt-image-1",          # DALL·E 3.5 / latest image model
        prompt=prompt,
        n=n_images,
        size="1024x1792",             # tall 9:16-ish
    )

    urls: List[str] = []
    for item in response.data:
        # Each item has .url for a temporary CDN URL
        if hasattr(item, "url") and item.url:
            urls.append(item.url)

    if not urls:
        raise RuntimeError("OpenAI image API returned no URLs")

    return urls