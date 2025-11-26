import os
import openai
from config import require_env

openai.api_key = require_env("OPENAI_API_KEY")

MODEL = "gpt-4o-mini-tts"    # Or your preferred TTS model
VOICE = "michelle"           # Michelle voice
SPEED = 1.2                  # 1.2x speed


def generate_tts_audio(text: str, output_path: str) -> str:
    """
    Generate TTS audio using OpenAI API.
    Returns the output_path to the generated audio file.
    """
    if not text.strip():
        raise ValueError("Empty transcript passed to TTS")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    response = openai.audio.speech.create(
        model=MODEL,
        voice=VOICE,
        speed=SPEED,
        input=text
    )

    with open(output_path, "wb") as f:
        f.write(response.read())

    return output_path