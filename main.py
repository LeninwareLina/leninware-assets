import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Local modules ---
from claude_client import get_claude_outputs
from tts_generator import generate_tts_audio

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Environment variables ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN env var is missing")


# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Leninware pipeline online.\n\n"
        "Commands:\n"
        "/ping - check if I'm alive\n"
        "/claude <youtube_url> - test Claude\n"
        "/tts <text> - test TTS\n"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PONG comrade.")


async def claude_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /claude <youtube_url>
    Calls Claude and returns tts_script, title, description.
    """
    if not context.args:
        await update.message.reply_text("Usage: /claude <YouTube URL>")
        return

    youtube_url = context.args[0]
    await update.message.reply_text("Asking Claude…")

    try:
        data = get_claude_outputs(youtube_url)
    except Exception as e:
        logger.exception("Claude call failed")
        await update.message.reply_text(f"Claude error: {e}")
        return

    tts_preview = (
        data["tts_script"][:500] + "…"
        if len(data["tts_script"]) > 500 else data["tts_script"]
    )

    reply = (
        f"*Title:*\n{data['title']}\n\n"
        f"*Description:*\n{data['description']}\n\n"
        f"*TTS script preview:*\n{tts_preview}"
    )

    await update.message.reply_markdown(reply)


async def tts_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /tts <text>
    Generates an MP3 clip using OpenAI TTS.
    """
    if not context.args:
        await update.message.reply_text("Usage: /tts comrades unite!")
        return

    text = " ".join(context.args)
    await update.message.reply_text("Generating Leninware TTS…")

    try:
        filepath = generate_tts_audio(text, "test_tts.mp3")
    except Exception as e:
        logger.exception("TTS failed")
        await update.message.reply_text(f"TTS error: {e}")
        return

    await update.message.reply_audio(audio=open(filepath, "rb"))


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command, comrade.")


# --- Main app ---
def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("claude", claude_test))
    application.add_handler(CommandHandler("tts", tts_test))

    # Catch unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Starting Telegram bot…")
    application.run_polling()


if __name__ == "__main__":
    main()