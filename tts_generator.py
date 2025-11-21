# tts_generator.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VOICE = "nova"          # your chosen voice
MODEL = "gpt-4o-mini-tts"
SPEED = 1.3             # 1.3x speed


def synthesize_speech(text: str) -> bytes:
    """
    Generate TTS audio for the given text and return raw audio bytes.
    """
    response = client.audio.speech.create(
        model=MODEL,
        voice=VOICE,
        input=text,
        speed=SPEED,
        response_format="mp3",   # important: use response_format, NOT format
    )

    # The Python SDK returns a streaming-like object; read() gives us the bytes
    audio_bytes = response.read()
    return audio_bytes