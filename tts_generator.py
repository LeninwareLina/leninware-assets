import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

_client = OpenAI(api_key=OPENAI_API_KEY)


def synthesize_speech(text: str) -> bytes:
    """
    Generate speech audio (mp3) from text using OpenAI TTS.
    Returns raw bytes.
    """
    resp = _client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    )
    return resp.read()