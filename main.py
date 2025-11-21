import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from youtube_transcript_fetcher import fetch_youtube_transcript
from youtube_metadata import fetch_youtube_metadata
from tts_generator import generate_tts
from claude_client import generate_leninware_output

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Leninware online ✊")


async def tts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /tts some text to speak")
        return

    text = " ".join(context.args)
    try:
        audio_bytes = generate_tts(text)
        await update.message.reply_voice(voice=audio_bytes)
    except Exception as e:
        await update.message.reply_text(f"TTS failed: {e}")


async def claude_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /Claude <YouTube URL>")
        return

    url = context.args[0]
    await update.message.reply_text("Fetching transcript via TranscriptAPI...")

    try:
        transcript, title, channel = fetch_youtube_transcript(url)
    except Exception as e:
        await update.message.reply_text(f"Could not get transcript: {e}")
        return

    # Fetch metadata separately (thumbnail, channel, etc.)
    try:
        metadata = fetch_youtube_metadata(url)
    except Exception:
        metadata = {"title": title, "channel": channel}

    try:
        output = generate_leninware_output(transcript, title, channel, metadata)
    except Exception as e:
        await update.message.reply_text(f"Claude generation failed: {e}")
        return

    await update.message.reply_text(output)


def main():
    application = ApplicationBuilder().token(TELEGRAM_API_KEY).build()

    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("tts", tts_command))
    application.add_handler(CommandHandler("Claude", claude_command))

    application.run_polling()


if __name__ == "__main__":
    main()