# image_generator.py

import base64
from pathlib import Path
from typing import List


OUTPUT_DIR = Path("generated_images")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_images(prompts: List[str]) -> List[str]:
    """
    Given a list of prompts, generate images and return a list of file paths.

    For now this is a stub: it just creates placeholder PNGs.
    You can later wire it to an actual image API or local model.
    """
    paths: List[str] = []

    if not prompts:
        return paths

    for i, prompt in enumerate(prompts, start=1):
        # Placeholder 1x1 transparent PNG
        img_bytes = base64.b64decode(
            b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAA"
            b"AAAC0lEQVR42mP8/x8AAwMCAO+cq3sAAAAASUVORK5CYII="
        )
        path = OUTPUT_DIR / f"leninware_{i}.png"
        path.write_bytes(img_bytes)
        paths.append(str(path))

    return paths