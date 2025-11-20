import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from claude_client import get_claude_output
from tts_generator import generate_tts_audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN env var is missing")


# ============ COMMAND HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Leninware pipeline online.\n\n"
        "Commands:\n"
        "/ping - check if I'm alive\n"
        "/claude <YouTube URL> - process video\n"
        "/tts <text> - generate speech test"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PONG — pipeline is running.")


async def claude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Claude generation: title, description, tts_script."""
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /claude <YouTube URL>")
        return

    youtube_url = context.args[0]
    await update.message.reply_text("Asking Claude...")

    try:
        data = get_claude_output(youtube_url)

        title = data.get("title", "")
        desc = data.get("description", "")
        script = data.get("tts_script", "")

        await update.message.reply_text(
            f"✔ *Claude Output Ready*\n\n"
            f"*Title:* {title}\n\n"
            f"*Description:* {desc}\n\n"
            f"*TTS Script:* {script[:500]}..."
            , parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"Claude error: {e}")


async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test TTS engine standalone."""
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /tts <text>")
        return

    text = " ".join(context.args)
    await update.message.reply_text("Generating Leninware TTS...")

    try:
        output_path = "test_tts.mp3"
        generate_tts_audio(text, output_path)
        await update.message.reply_audio(audio=open(output_path, "rb"))

    except Exception as e:
        await update.message.reply_text(f"TTS error: {e}")


# ============ MAIN APPLICATION ============

def main():
    logger.info("Starting Telegram bot...")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("claude", claude))
    app.add_handler(CommandHandler("tts", tts))

    logger.info("Application started.")
    app.run_polling()


if __name__ == "__main__":
    main()