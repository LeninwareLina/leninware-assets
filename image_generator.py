# image_generator.py
import os
import base64

from config import USE_MOCK_AI, require_env

# Only import OpenAI if NOT in mock mode
if not USE_MOCK_AI:
    from openai import OpenAI

MODEL = "gpt-image-1"  # or whichever model you're using


def generate_images_from_prompts(prompts: list[str]) -> list[str]:
    """Generate images silently from a list of prompts.
       Returns a list of saved file paths.
    """

    if not prompts:
        raise ValueError("No prompts passed to image generator")

    output_dir = "output/images"
    os.makedirs(output_dir, exist_ok=True)

    image_paths = []

    # ----------------------------------------------------
    # MOCK MODE (no cost, no API calls)
    # ----------------------------------------------------
    if USE_MOCK_AI:
        for i, prompt in enumerate(prompts, start=1):
            img_path = os.path.join(output_dir, f"frame_{i}.png")

            # Create a tiny 1×1 transparent PNG
            transparent_png = (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
                b'\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06'
                b'\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00'
                b'\x0cIDATx\x9cc`\x00\x00\x00\x02\x00\x01'
                b'\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'
            )

            with open(img_path, "wb") as f:
                f.write(transparent_png)

            image_paths.append(img_path)

        return image_paths

    # ----------------------------------------------------
    # REAL MODE (OpenAI images.generate)
    # ----------------------------------------------------
    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

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
            print(f"[image_generator] Error on prompt {i}: {e}")

    return image_paths