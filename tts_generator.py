import os
from openai import OpenAI


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

client = OpenAI(api_key=OPENAI_API_KEY)


def synthesize_speech(text: str) -> bytes:
    """
    Returns MP3 audio bytes for the given text.
    """
    resp = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
        format="mp3",
    )
    # The OpenAI Python 1.x client returns a streaming-like object
    return resp.read()