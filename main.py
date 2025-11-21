# main.py
import os
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from telegram_handlers import handle_youtube

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("Leninware online ✊")

def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN missing")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube))

    app.run_polling()

if __name__ == "__main__":
    main()