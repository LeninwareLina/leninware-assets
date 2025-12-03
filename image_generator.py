# image_generator.py

import os
import base64

from config import USE_MOCK_AI, require_env

# Only import OpenAI if NOT in mock mode
if not USE_MOCK_AI:
    from openai import OpenAI

MODEL = "gpt-image-1"  # or whichever model you're using


def generate_images_from_prompts(prompts: list[str]) -> list[str]:
    """
    Generate images from prompts (mock or real), with full debug logging.
    Returns a list of saved file paths.
    """

    print(f"[image] Starting image generation — {len(prompts)} prompts")

    if not prompts:
        print("[image] ERROR — No prompts passed to image generator")
        raise ValueError("No prompts passed to image generator")

    output_dir = "output/images"
    os.makedirs(output_dir, exist_ok=True)
    print(f"[image] Output directory ready: {output_dir}")

    image_paths = []

    # ----------------------------------------------------
    # MOCK MODE — free tiny PNGs
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print("[image:mock] Mock mode enabled — generating transparent PNGs")

        transparent_png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
            b'\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06'
            b'\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00'
            b'\x0cIDATx\x9cc`\x00\x00\x00\x02\x00\x01'
            b'\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'
        )

        for i, prompt in enumerate(prompts, start=1):
            print(f"[image:mock] Creating mock frame {i} from prompt (len={len(prompt)})")

            img_path = os.path.join(output_dir, f"frame_{i}.png")
            try:
                with open(img_path, "wb") as f:
                    f.write(transparent_png)
                print(f"[image:mock] Saved mock image → {img_path}")
                image_paths.append(img_path)

            except Exception as e:
                print(f"[image:mock] ERROR saving mock image {i}: {e}")

        print(f"[image:mock] Completed generating {len(image_paths)} mock images")
        return image_paths

    # ----------------------------------------------------
    # REAL MODE — OpenAI Images API
    # ----------------------------------------------------
    print("[image] Real mode enabled — Calling OpenAI image model")
    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    for i, prompt in enumerate(prompts, start=1):
        print(f"[image] Generating image {i}/{len(prompts)}")
        print(f"[image] Prompt length: {len(prompt)} chars")

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

            print(f"[image] Saved frame {i} → {img_path}")
            image_paths.append(img_path)

        except Exception as e:
            print(f"[image] ERROR generating image {i}: {e}")

    print(f"[image] Finished generating {len(image_paths)} images total")
    return image_paths