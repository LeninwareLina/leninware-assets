# telegram_handlers.py
from telegram import Update
from telegram.ext import ContextTypes
from youtube_transcript_fetcher import fetch_transcript
from claude_client import run_claude
import os

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()

    # Extract video URL
    url = None
    for token in message.split():
        if "youtube.com" in token or "youtu.be" in token:
            url = token
            break

    if not url:
        await update.message.reply_text("Send a YouTube link.")
        return

    await update.message.reply_text("Fetching transcript via TranscriptAPI...")

    try:
        transcript = fetch_transcript(url)
    except Exception as e:
        await update.message.reply_text(f"Could not get transcript: {e}")
        return

    await update.message.reply_text("Transcript received. Sending to Claude...")

    try:
        result = await run_claude(transcript, CLAUDE_API_KEY)
    except Exception as e:
        await update.message.reply_text(f"Claude error: {e}")
        return

    await update.message.reply_text(result)