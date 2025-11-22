# main.py
import os
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram_handlers import handle_youtube

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Telegram token
BOT_TOKEN = os.getenv("TELEGRAM_API_KEY") or os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Leninware online.\nSend a YouTube link to begin."
    )


async def ping(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong ✊")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Missing TELEGRAM_API_KEY")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))

    # Automatically detect YouTube URLs in ANY message
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube)
    )

    logger.info("Leninware bot starting…")
    app.run_polling()


if __name__ == "__main__":
    main()