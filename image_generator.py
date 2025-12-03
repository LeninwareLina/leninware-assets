# image_generator.py
import os
import base64
from openai import OpenAI
from config import require_env

MODEL = "gpt-image-1"  # or whichever model you're using


def generate_images_from_prompts(prompts: list[str]) -> list[str]:
    """Generate images silently from a list of prompts.
       Returns a list of saved file paths.
    """

    if not prompts:
        raise ValueError("No prompts passed to image generator")

    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    output_dir = "output/images"
    os.makedirs(output_dir, exist_ok=True)

    image_paths = []

    for i, prompt in enumerate(prompts, start=1):
        try:
            resp = client.images.generate(
                model=MODEL,
                prompt=prompt,
                size="1024x1024"
            )

            image_base64 = resp.data[0].b64_json

            img_path = os.path.join(output_dir, f"frame_{i}.png")
            with open(img_path, "wb") as img_file:
                img_file.write(base64.b64decode(image_base64))

            image_paths.append(img_path)

        except Exception as e:
            # Only error printed to logs
            print(f"[image_generator] Error on prompt {i}: {e}")

    return image_paths