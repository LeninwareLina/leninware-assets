import io
import logging
import os

from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from youtube_transcript_fetcher import fetch_transcript_via_service, TranscriptError
from youtube_metadata import fetch_youtube_metadata
from claude_client import generate_leninware_from_payload, ClaudeError
from tts_generator import generate_tts, TTSError


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_API_KEY")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Leninware online.\n\n"
        "/ping – check if I'm alive\n"
        "/tts <text> – generate TTS using OpenAI\n"
        "/Claude <YouTube URL> – pull captions and run Leninware analysis"
    )
    await update.message.reply_text(text)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Leninware online ✊")


async def tts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /tts some text to speak")
        return

    try:
        audio_bytes = generate_tts(text)
    except TTSError as e:
        logger.exception("TTS failed")
        await update.message.reply_text(f"TTS failed: {e}")
        return
    except Exception as e:
        logger.exception("TTS failed (unexpected)")
        await update.message.reply_text(f"TTS failed: {e}")
        return

    bio = io.BytesIO(audio_bytes)
    bio.name = "speech.mp3"
    await update.message.reply_voice(voice=InputFile(bio))


async def claude_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /Claude <YouTube URL>")
        return

    video_url = context.args[0]

    await update.message.reply_text("Fetching transcript via TranscriptAPI...")

    try:
        transcript_text = fetch_transcript_via_service(video_url)
    except TranscriptError as e:
        logger.warning("Transcript fetch failed: %s", e)
        await update.message.reply_text(f"Could not get transcript: {e}")
        return

    meta = fetch_youtube_metadata(video_url)

    payload = {
        "transcript": transcript_text,
        "video_title": meta.title,
        "channel_name": meta.channel_name,
        "video_url": video_url,
    }

    await update.message.reply_text("Asking Claude (Leninware mode)…")

    try:
        outputs = generate_leninware_from_payload(payload)
    except ClaudeError as e:
        logger.exception("Claude processing failed")
        await update.message.reply_text(f"Claude failed: {e}")
        return

    reply = (
        "TTS SCRIPT:\n"
        f"{outputs['tts']}\n\n"
        "TITLE:\n"
        f"{outputs['title']}\n\n"
        "DESCRIPTION:\n"
        f"{outputs['description']}"
    )
    await update.message.reply_text(reply)

    try:
        audio_bytes = generate_tts(outputs["tts"])
        bio = io.BytesIO(audio_bytes)
        bio.name = "leninware_commentary.mp3"
        await update.message.reply_voice(voice=InputFile(bio))
    except Exception as e:
        logger.exception("Post-Claude TTS failed")
        # Not fatal.


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Missing TELEGRAM_API_KEY environment variable")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("tts", tts_command))
    app.add_handler(CommandHandler("Claude", claude_command))

    logger.info("Starting Leninware bot…")
    app.run_polling()


if __name__ == "__main__":
    main()