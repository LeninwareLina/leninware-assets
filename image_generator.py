# image_generator.py

from pathlib import Path
from typing import List
import base64
from openai import OpenAI
from config import require_env

OUTPUT_DIR = Path("generated_images")
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_images_from_prompts(prompts: List[str]) -> List[str]:
    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    paths = []
    for i, prompt in enumerate(prompts, start=1):
        print(f"[images] Generating image {i}/{len(prompts)}")
        print(prompt)

        resp = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            n=1,
        )

        b64 = resp.data[0].b64_json
        img = base64.b64decode(b64)

        path = OUTPUT_DIR / f"storyboard_{i}.png"
        path.write_bytes(img)
        paths.append(str(path))

    return paths