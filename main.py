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

# --- Logging so we can see what's going on in Railway logs ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Read token from environment ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN env var is missing")


# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Leninware pipeline online.\n\n"
        "Commands:\n"
        "/ping - check if I'm alive\n"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PONG – pipeline is running.")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This will catch any unknown /commands
    await update.message.reply_text("I don't know that command yet.")


def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Known commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))

    # Catch-all for unknown commands like /whatever
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    main()