import os

from openai import OpenAI

from config import require_env

# TTS model + voice config
MODEL = "gpt-4o-mini-tts"
VOICE = "marin"
SPEED = 1.2  # 1.2x speed


def generate_tts_audio(text: str, output_path: str) -> str:
    """Generate TTS audio using OpenAI's speech API.

    Returns:
        Path to the generated audio file.
    """
    if not text or not text.strip():
        raise ValueError("Empty transcript passed to TTS")

    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    response = client.audio.speech.create(
        model=MODEL,
        voice=VOICE,
        speed=SPEED,
        input=text,
    )

    # In current OpenAI client, write_to_file is usually available
    if hasattr(response, "write_to_file"):
        response.write_to_file(output_path)
    else:
        # Fallback: assume file-like object with .read()
        with open(output_path, "wb") as f:
            f.write(response.read())

    return output_path