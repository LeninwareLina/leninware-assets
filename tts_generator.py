import os
from openai import OpenAI


class TTSError(Exception):
    """Raised when text-to-speech generation fails."""
    pass


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_tts(text: str) -> bytes:
    """
    Generate TTS audio using OpenAI's nova voice, 1.3x speed.
    Returns audio bytes (MP3).
    """
    try:
        result = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="nova",
            speed=1.3,
            input=text,
        )

        return result.read()

    except Exception as e:
        raise TTSError(str(e)) from e