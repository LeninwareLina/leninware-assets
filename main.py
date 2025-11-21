import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from youtube_transcript_fetcher import fetch_transcript_via_service, TranscriptError
from claude_client import run_claude
from tts_generator import generate_tts, TTSError

logging.basicConfig(level=logging.INFO)

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")

# -------------------------------------------------------------
# /ping — basic bot check
# -------------------------------------------------------------
async def ping(update, context):
    await update.message.reply_text("Leninware online ✊")

# -------------------------------------------------------------
# /tts <text>
# -------------------------------------------------------------
async def tts_command(update, context):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /tts <text>")
        return

    try:
        audio_path = generate_tts(text)
        with open(audio_path, "rb") as audio:
            await update.message.reply_voice(voice=audio)
    except TTSError as e:
        await update.message.reply_text(f"TTS failed: {e}")

# -------------------------------------------------------------
# /Claude <YouTube URL>
# -------------------------------------------------------------
async def claude_command(update, context):
    if not context.args:
        await update.message.reply_text("Send a YouTube URL.")
        return

    url = context.args[0].strip()
    await update.message.reply_text("Fetching transcript via TranscriptAPI...")

    # ---------------------------------------------------------
    # FETCH TRANSCRIPT
    # ---------------------------------------------------------
    try:
        transcript_text = fetch_transcript_via_service(url)
    except TranscriptError as e:
        await update.message.reply_text(
            f"Could not get transcript: {e}. No Leninware outputs can be produced."
        )
        return

    # ---------------------------------------------------------
    # SEND TO CLAUDE
    # ---------------------------------------------------------
    try:
        response = run_claude(transcript_text)
    except Exception as e:
        await update.message.reply_text(f"Claude failed: {e}")
        return

    # ---------------------------------------------------------
    # Claude reply (text)
    # ---------------------------------------------------------
    await update.message.reply_text(response)

    # ---------------------------------------------------------
    # TTS generation (Nova, 1.3× speed as already configured)
    # ---------------------------------------------------------
    try:
        audio_path = generate_tts(response)
        with open(audio_path, "rb") as audio:
            await update.message.reply_voice(voice=audio)
    except TTSError:
        await update.message.reply_text("TTS failed, but text output succeeded.")

# -------------------------------------------------------------
# BOT STARTUP
# -------------------------------------------------------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_API_KEY).build()

    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("tts", tts_command))
    app.add_handler(CommandHandler("Claude", claude_command))

    app.run_polling()

if __name__ == "__main__":
    main()