#audio_generator.py
import os
import wave

from config import USE_MOCK_AI, require_env

# Only import OpenAI if NOT in mock mode
if not USE_MOCK_AI:
    from openai import OpenAI

# TTS model + voice config
MODEL = "gpt-4o-mini-tts"
VOICE = "marin"
SPEED = 1.2  # 1.2x speed


def generate_tts_audio(text: str, output_path: str) -> str:
    """Generate TTS audio (real or mock)."""

    if USE_MOCK_AI:
        # ----------------------------------------------------
        # MOCK MODE → generate a tiny silent WAV file (free)
        # ----------------------------------------------------
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with wave.open(output_path, "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(16000)
            wav.writeframes(b"\x00\x00" * 4000)  # 0.25s silence

        return output_path

    # ----------------------------------------------------
    # REAL TTS MODE → uses OpenAI API (costs money)
    # ----------------------------------------------------
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

    if hasattr(response, "write_to_file"):
        response.write_to_file(output_path)
    else:
        with open(output_path, "wb") as f:
            f.write(response.read())

    return output_path