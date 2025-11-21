# main.py
import os
import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram_handlers import handle_youtube

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def incoming(update, context):
    text = update.message.text
    reply = handle_youtube(text)
    await update.message.reply_text(reply)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, incoming)
    )

    application.run_polling()

if __name__ == "__main__":
    main()