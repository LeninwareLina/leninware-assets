# main.py
import os
from telegram.ext import ApplicationBuilder, CommandHandler
from claude_client import claude_ping

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("Bot online. Use /claude_ping")

async def test_claude(update, context):
    try:
        result = claude_ping()
        await update.message.reply_text(f"Claude says: {result}")
    except Exception as e:
        await update.message.reply_text(f"Claude error: {e}")

def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN missing")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("claude_ping", test_claude))

    app.run_polling()

if __name__ == "__main__":
    main()