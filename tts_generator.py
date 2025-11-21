import io
import os

from openai import OpenAI
from openai import APIError as OpenAIAPIError

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class TTSError(Exception):
    """Raised when TTS generation fails."""


def _get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise TTSError("OPENAI_API_KEY environment variable is not set.")
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_tts(text: str) -> io.BytesIO:
    """
    Generate speech audio from text using OpenAI TTS.

    - Voice: nova
    - Speed: 1.3x
    - Returns a BytesIO with mp3 data, ready to send via Telegram.
    """
    if not text.strip():
        raise TTSError("TTS text is empty.")

    client = _get_client()

    try:
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="nova",
            input=text,
            speed=1.3,  # your preferred 1.3x speed
        )
    except OpenAIAPIError as e:
        raise TTSError(f"OpenAI TTS API error: {e}") from e
    except Exception as e:
        raise TTSError(f"Unexpected OpenAI TTS error: {e}") from e

    # New OpenAI client: response is a binary-like object
    try:
        audio_bytes = response.read()
    except AttributeError:
        # Some client versions expose .content instead
        audio_bytes = getattr(response, "content", None)
        if audio_bytes is None:
            raise TTSError("OpenAI TTS returned no audio bytes.")

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "leninware_tts.mp3"
    audio_file.seek(0)
    return audio_file