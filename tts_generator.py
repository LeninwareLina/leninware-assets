import os
import tempfile
from openai import OpenAI


class TTSError(Exception):
    """Raised when TTS generation fails."""
    pass


# Expect OPENAI_API_KEY in env
_openai_api_key = os.getenv("OPENAI_API_KEY")
if not _openai_api_key:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

_client = OpenAI(api_key=_openai_api_key)


def generate_tts(text: str) -> str:
    """
    Generate speech audio for the given text using OpenAI TTS.

    Returns:
        Path to a temporary MP3 file containing the audio.
    """
    if not text or not text.strip():
        raise TTSError("No text provided for TTS")

    try:
        response = _client.audio.speech.create(
            model="gpt-4o-mini-tts",  # TTS-capable model
            voice="nova",             # your preferred voice
            input=text,
            speed=1.3,                # 1.3x speed as you requested
        )

        # For the Python client, .create(...) returns a BinaryIO-like object
        audio_bytes = response.read()

        fd, path = tempfile.mkstemp(suffix=".mp3")
        with os.fdopen(fd, "wb") as f:
            f.write(audio_bytes)

        return path
    except Exception as e:
        raise TTSError(f"TTS generation failed: {e}")