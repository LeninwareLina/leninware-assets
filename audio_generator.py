# audio_generator.py

import os
import wave

from config import USE_MOCK_AI, LANGUAGE_MODE, require_env

# Only import OpenAI in real mode
if not USE_MOCK_AI:
    from openai import OpenAI

# Base TTS model
MODEL = "gpt-4o-mini-tts"

# Voice selection by language
VOICE_EN = "marin"       # English — good clarity and tone
VOICE_ES = "sofia"       # Spanish Latin American voice (best for Argentina)

SPEED = 1.2  # 1.2x speed for snappy commentary


def _select_voice() -> str:
    """Choose voice based on LANGUAGE_MODE."""
    if LANGUAGE_MODE == "es":
        print("[tts] LANGUAGE_MODE=es → Using Spanish voice 'sofia'")
        return VOICE_ES
    else:
        print("[tts] LANGUAGE_MODE=en → Using English voice 'marin'")
        return VOICE_EN


def generate_tts_audio(text: str, output_path: str) -> str:
    """
    Generate TTS audio (real or mock), with full debug logging.
    """
    print(f"[tts] Starting TTS generation → output: {output_path}")

    # Select correct voice
    voice = _select_voice()

    # ----------------------------------------------------
    # MOCK MODE — create a tiny silent WAV file
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print("[tts:mock] Mock mode enabled — generating silent WAV instead of calling OpenAI")

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with wave.open(output_path, "w") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(16000)
                wav.writeframes(b"\x00\x00" * 4000)  # ~0.25s silence

            print(f"[tts:mock] Mock WAV created successfully ({output_path})")
        except Exception as e:
            print(f"[tts:mock] ERROR creating mock WAV: {e}")
            return None

        return output_path

    # ----------------------------------------------------
    # REAL MODE — call OpenAI TTS API
    # ----------------------------------------------------
    if not text or not text.strip():
        print("[tts] ERROR — empty script passed to TTS")
        raise ValueError("Empty transcript passed to TTS")

    print("[tts] Real TTS mode — calling OpenAI API")
    print(f"[tts] Model={MODEL}, Voice={voice}, Speed={SPEED}")

    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        response = client.audio.speech.create(
            model=MODEL,
            voice=voice,
            speed=SPEED,
            input=text,
        )

        if hasattr(response, "write_to_file"):
            response.write_to_file(output_path)
        else:
            with open(output_path, "wb") as f:
                f.write(response.read())

        print(f"[tts] TTS audio saved successfully: {output_path}")

    except Exception as e:
        print(f"[tts] ERROR during real TTS generation: {e}")
        return None

    return output_path