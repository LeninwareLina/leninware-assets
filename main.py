import logging
import os
import re

from telegram import ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
)

from youtube_transcript_fetcher import fetch_transcript_via_transcriptapi, TranscriptError
from claude_client import generate_leninware_outputs, ClaudeError
from tts_generator import generate_tts, TTSError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_API_KEY")

YOUTUBE_URL_RE = re.compile(
    r"(https?://(?:www\.)?"
    r"(?:youtube\.com/watch\?v=[\w\-]+[^\s]*|youtu\.be/[\w\-]+[^\s]*))"
)


def start(update, context):
    update.message.reply_text(
        "Leninware online ✊\n\n"
        "Commands:\n"
        "/ping – check status\n"
        "/tts <text> – speak text\n"
        "/Claude <YouTube URL> – Leninware analysis pipeline"
    )


def ping(update, context):
    update.message.reply_text("Leninware online ✊")


def tts_command(update, context):
    args_text = " ".join(context.args).strip()
    if not args_text:
        update.message.reply_text("Usage: /tts some text to speak")
        return

    try:
        audio_file = generate_tts(args_text)
    except TTSError as e:
        logger.exception("TTS failed")
        update.message.reply_text(f"TTS failed: {e}")
        return

    chat_id = update.message.chat_id
    context.bot.send_audio(chat_id=chat_id, audio=audio_file, title="Leninware TTS")


def claude_command(update, context):
    if not context.args:
        update.message.reply_text("Usage: /Claude <YouTube URL>")
        return

    url_candidate = context.args[0].strip()
    m = YOUTUBE_URL_RE.search(url_candidate)
    if not m:
        update.message.reply_text("Please provide a valid YouTube URL.")
        return

    video_url = m.group(1)
    chat_id = update.message.chat_id

    status_msg = update.message.reply_text(
        "Fetching transcript via TranscriptAPI..."
    )

    # 1) Get transcript
    try:
        transcript_md = fetch_transcript_via_transcriptapi(video_url)
    except TranscriptError as e:
        logger.exception("Transcript fetch failed")
        status_msg.edit_text(f"Could not get transcript: {e}")
        return

    status_msg.edit_text("Transcript fetched. Generating Leninware outputs via Claude...")

    # 2) Ask Claude for Leninware outputs
    try:
        outputs = generate_leninware_outputs(transcript_md)
    except ClaudeError as e:
        logger.exception("Claude generation failed")
        status_msg.edit_text(f"Claude generation failed: {e}")
        return

    title = outputs.get("title", "Leninware Analysis")
    description = outputs.get("description", "No description.")
    tts_script = outputs.get("tts_script", "")

    # 3) Send title + description
    text_message = (
        "*OUTPUT 1 — TITLE*\n"
        f"{title}\n\n"
        "*OUTPUT 2 — DESCRIPTION*\n"
        f"{description}"
    )

    context.bot.send_message(
        chat_id=chat_id,
        text=text_message,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=False,
    )

    # 4) Optionally generate and send TTS for the Leninware monologue
    if tts_script.strip():
        try:
            audio_file = generate_tts(tts_script)
            context.bot.send_audio(
                chat_id=chat_id,
                audio=audio_file,
                title="OUTPUT 3 — Leninware TTS",
            )
        except TTSError as e:
            logger.exception("TTS failed for Leninware script")
            context.bot.send_message(
                chat_id=chat_id, text=f"TTS failed for Leninware script: {e}"
            )


def error_handler(update, context):
    logger.exception("Unhandled error while processing update: %s", context.error)


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_API_KEY environment variable is not set.")

    # Legacy-style bot (v13 compatible)
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("tts", tts_command))
    dp.add_handler(CommandHandler("Claude", claude_command))

    dp.add_error_handler(error_handler)

    logger.info("Leninware bot starting (legacy telegram-telegram-bot v13 compatible)...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()