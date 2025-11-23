# image_generator.py

import base64
from typing import List
from pathlib import Path

from openai import OpenAI
from config import OPENAI_API_KEY, require_env


def generate_images(prompts: List[str], output_dir: str = "generated_images") -> List[str]:
    """
    Uses OpenAI Images API to generate one image per prompt.
    Returns list of file paths.

    NOTE: Keep this cheap by limiting resolution and count.
    """
    require_env("OPENAI_API_KEY", OPENAI_API_KEY)
    client = OpenAI(api_key=OPENAI_API_KEY)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = []

    for i, prompt in enumerate(prompts):
        resp = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        b64_data = resp.data[0].b64_json
        img_bytes = base64.b64decode(b64_data)

        path = out_dir / f"leninware_{i+1}.png"
        path.write_bytes(img_bytes)
        paths.append(str(path))

    return paths