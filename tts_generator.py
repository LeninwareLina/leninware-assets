import os
import io

from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class TTSError(Exception):
    """Raised when TTS generation fails."""


def _get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise TTSError("Missing OPENAI_API_KEY environment variable")
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_tts(text: str) -> bytes:
    """
    Generate speech audio (MP3) from text using OpenAI TTS.

    Returns raw MP3 bytes.
    """
    if not text or not text.strip():
        raise TTSError("Refusing to synthesize empty text")

    client = _get_client()

    # Use nova voice; instruct for ~1.3x speed.
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="nova",
        input=text,
        instructions="Speak about 1.3x faster than a typical narration, "
                     "with clear, intense delivery.",
    )

    buf = io.BytesIO()
    for chunk in response.iter_bytes():
        buf.write(chunk)
    return buf.getvalue()