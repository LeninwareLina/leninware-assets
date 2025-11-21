import logging
import os
import tempfile

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)

from tts_generator import generate_tts, TTSError
from youtube_transcript_fetcher import fetch_transcript_via_service, TranscriptError
from claude_client import generate_leninware_from_transcript, ClaudeError


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing {name} environment variable")
    return value


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Leninware online ✊")


def ping(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Leninware online ✊")


def tts_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text("Usage: /tts some text to speak")
        return

    text = " ".join(context.args).strip()
    if not text:
        update.message.reply_text("Usage: /tts some text to speak")
        return

    try:
        audio_path = generate_tts(text)
    except TTSError as e:
        logger.exception("TTS failed")
        update.message.reply_text(f"TTS failed: {e}")
        return

    try:
        with open(audio_path, "rb") as f:
            # Use send_audio so mp3 is fine
            update.message.reply_audio(audio=f)
    finally:
        try:
            os.remove(audio_path)
        except OSError:
            pass


def _send_long_message(update: Update, text: str) -> None:
    """
    Telegram has a ~4096 char limit per message.
    Split into chunks if needed.
    """
    max_len = 4000
    while text:
        chunk = text[:max_len]
        update.message.reply_text(chunk)
        text = text[max_len:]


def claude_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text("Usage: /Claude <YouTube URL or video ID>")
        return

    url_or_id = context.args[0].strip()
    update.message.reply_text("Fetching transcript via TranscriptAPI...")

    try:
        transcript, title, channel, canonical_url = fetch_transcript_via_service(url_or_id)
    except TranscriptError as e:
        # Match the phrasing your Claude prompt expects when no transcript exists
        msg = str(e)
        logger.warning("Transcript error: %s", msg)
        update.message.reply_text(f"Could not get transcript: {msg}")
        return

    payload = {
        "transcript": transcript,
        "video_title": title,
        "channel_name": channel,
        "video_url": canonical_url,
    }

    try:
        analysis = generate_leninware_from_transcript(payload)
    except ClaudeError as e:
        logger.exception("Claude generation failed")
        update.message.reply_text(f"Claude generation failed: {e}")
        return

    if not analysis.strip():
        update.message.reply_text("Claude returned an empty response.")
        return

    _send_long_message(update, analysis)


def main() -> None:
    token = _get_required_env("TELEGRAM_API_KEY")

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("tts", tts_command))
    dp.add_handler(CommandHandler("Claude", claude_command))

    logger.info("Leninware bot starting...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()