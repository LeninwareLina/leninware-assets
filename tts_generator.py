import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")  # or "tts-1"
TTS_VOICE = os.getenv("TTS_VOICE", "alloy")  # you can change this later

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

_client = OpenAI(api_key=OPENAI_API_KEY)


def synthesize_speech(text: str) -> bytes:
    """
    Generate speech audio (mp3) from text using OpenAI TTS.
    Returns raw bytes.
    """
    resp = _client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text,
    )
    # Streaming API: read all bytes
    return resp.read()