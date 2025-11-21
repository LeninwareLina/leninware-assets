import io
import logging
import os

from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from youtube_transcript import fetch_youtube_transcript
from claude_client import generate_leninware_from_transcript
from tts_generator import synthesize_speech

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
        "/youtube <url or video_id> – pull captions and run Leninware analysis"
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
        audio_bytes = synthesize_speech(text)
    except Exception as e:
        logger.exception("TTS failed")
        await update.message.reply_text(f"TTS failed: {e}")
        return

    bio = io.BytesIO(audio_bytes)
    bio.name = "speech.mp3"
    await update.message.reply_voice(voice=InputFile(bio))


async def youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /youtube <YouTube URL or video ID>")
        return

    url_or_id = context.args[0]

    await update.message.reply_text("Fetching YouTube captions…")

    try:
        transcript_text = fetch_youtube_transcript(url_or_id)
    except Exception as e:
        logger.exception("Transcript fetch failed")
        await update.message.reply_text(f"Could not get captions: {e}")
        return

    await update.message.reply_text("Asking Claude (Leninware mode)…")

    try:
        outputs = generate_leninware_from_transcript(transcript_text)
    except Exception as e:
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


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Missing TELEGRAM_API_KEY environment variable")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("tts", tts_command))
    app.add_handler(CommandHandler("youtube", youtube_command))

    logger.info("Starting Leninware bot…")
    app.run_polling()


if __name__ == "__main__":
    main()