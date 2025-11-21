import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from youtube_transcript_fetcher import get_transcript, TranscriptError
from claude_client import run_claude
from tts_client import generate_tts


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------------------
# Command: /start
# ---------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me any YouTube link and I will generate Leninware outputs."
    )


# ---------------------
# Handle YouTube URLs
# ---------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "youtu" not in text:
        await update.message.reply_text("Please send a valid YouTube link.")
        return

    video_url = text

    # 1️⃣ Fetch transcript via TranscriptAPI
    await update.message.reply_text("Fetching transcript via TranscriptAPI...")

    try:
        transcript_text = get_transcript(video_url)
    except TranscriptError as e:
        await update.message.reply_text(f"Could not get transcript: {e}")
        return

    # 2️⃣ Send transcript into Claude to generate Leninware outputs
    await update.message.reply_text("Processing with Claude...")

    try:
        result = await run_claude(transcript_text)
        title = result["title"]
        description = result["description"]
        tts_script = result["tts_script"]
    except Exception as e:
        logger.exception("Claude error")
        await update.message.reply_text(f"Claude error: {e}")
        return

    # 3️⃣ Generate TTS from the tts_script
    await update.message.reply_text("Generating TTS...")

    try:
        audio_bytes = await generate_tts(tts_script)
    except Exception as e:
        logger.exception("TTS error")
        await update.message.reply_text(f"TTS generation error: {e}")
        return

    # 4️⃣ Send Linuxware outputs back to Telegram
    await update.message.reply_text(f"📌 *{title}*\n\n{description}", parse_mode="Markdown")

    await update.message.reply_audio(audio=audio_bytes, filename="output.mp3")


# ---------------------
# Start bot
# ---------------------
def main():
    telegram_api_key = os.getenv("TELEGRAM_API_KEY")
    if not telegram_api_key:
        raise RuntimeError("Missing TELEGRAM_API_KEY")

    app = ApplicationBuilder().token(telegram_api_key).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started.")
    app.run_polling()


if __name__ == "__main__":
    main()