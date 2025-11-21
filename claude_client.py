# claude_client.py
import asyncio
from anthropic import Anthropic

async def run_claude(transcript: str, api_key: str) -> str:
    """
    Sends transcript to Claude and gets Leninware-style outputs back.
    """
    client = Anthropic(api_key=api_key)

    system_prompt = """
You are Leninware, a militant Marxist-Leninist analytic machine.
You generate three outputs:
1. A short viral-style TITLE.
2. A short DESCRIPTION.
3. A fiery, punchy TTS SCRIPT (60–120 seconds).

If transcript is missing or empty, respond exactly:
"Transcript unavailable. No Leninware outputs can be produced."
    """

    user_prompt = f"""
Here is the transcript from a YouTube video. Analyze it and produce:
TITLE:
DESCRIPTION:
TTS_SCRIPT:

Transcript:
{transcript}
"""

    response = await asyncio.to_thread(
        client.messages.create,
        model="claude-3-sonnet-20240229",
        max_tokens=800,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    return response.content[0].text