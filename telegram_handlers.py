# telegram_handlers.py
import re
from youtube_transcript_fetcher import fetch_transcript
from claude_client import generate_leninware_response

YOUTUBE_REGEX = r"(?:https?://)?(?:www\.)?youtu(?:be\.com/watch\?v=|\.be/)([\w-]{11})"

def extract_youtube_video_id(url: str):
    match = re.search(YOUTUBE_REGEX, url)
    return match.group(1) if match else None

def handle_youtube(message_text: str) -> str:
    video_id = extract_youtube_video_id(message_text)
    if not video_id:
        return "No valid YouTube URL detected."

    full_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        transcript = fetch_transcript(full_url)
    except Exception as e:
        return f"Transcript unavailable: {e}"

    # Channel name placeholder — Telegram does not always provide it
    channel = "channel"

    result = generate_leninware_response(transcript, full_url, channel)

    message = (
        f"🎤 *TTS Script*:\n{result['tts']}\n\n"
        f"📛 *Title*:\n{result['title']}\n\n"
        f"📄 *Description*:\n{result['description']}"
    )

    return message