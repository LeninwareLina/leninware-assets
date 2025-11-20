import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY env var is missing")

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_tts_audio(tts_script: str, output_path="tts_output.mp3") -> str:
    """
    Generate TTS audio using OpenAI's voice.
    We use:
      - model: gpt-4o-mini-tts
      - voice: alloy (female-leaning voice)
      - speed: 1.2x (fast pacing for Shorts)
    Saves output to a file and returns the path.
    """

    logger.info("Generating TTS audio at 1.2x speed...")

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",      # female-type voice
        input=tts_script,
        speed=1.2,
        format="mp3"
    )

    audio_bytes = response.read()

    with open(output_path, "wb") as f:
        f.write(audio_bytes)

    logger.info(f"TTS saved: {output_path}")
    return output_path