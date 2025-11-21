# claude_client.py
import asyncio
from anthropic import AsyncAnthropic

# ----------------------------
#  LENINWARE SYSTEM PROMPT
# ----------------------------
LENINWARE_SYSTEM_PROMPT = """
SYSTEM MODE: LENINWARE (ACTIVE)

You operate in Leninware Mode, a materialist, anti-liberal, anti-imperialist analytical mode…
[YOUR FULL PROMPT HERE — unchanged]
"""


async def run_claude(transcript: str, api_key: str) -> dict:
    """
    Sends transcript to Claude (Sonnet 3) and returns:
    {
        "title": "...",
        "description": "...",
        "tts_script": "..."
    }
    """

    client = AsyncAnthropic(api_key=api_key)

    user_prompt = f"""
You will now apply Leninware Mode to the transcript below and produce:

1. TITLE
2. DESCRIPTION
3. TTS_SCRIPT

Transcript:
{transcript}
"""

    # ----------------------------
    #  CALL CLAUDE
    # ----------------------------
    response = await client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1800,
        system=LENINWARE_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": user_prompt}]
            }
        ]
    )

    # Claude returns its entire output as one block of text
    text = response.content[0].text

    # ----------------------------
    #  SIMPLE PARSER
    # ----------------------------
    title = ""
    desc = ""
    tts = ""

    lower = text.lower()

    if "title:" in lower:
        try:
            title = text.split("TITLE:", 1)[1].split("\n", 1)[0].strip()
        except:
            title = ""

    if "description:" in lower:
        try:
            desc = text.split("DESCRIPTION:", 1)[1].split("TTS_SCRIPT:", 1)[0].strip()
        except:
            desc = text

    if "tts_script:" in lower:
        try:
            tts = text.split("TTS_SCRIPT:", 1)[1].strip()
        except:
            tts = text

    # fallback: return raw
    if not title:
        title = "Generated Title"

    if not desc:
        desc = text

    if not tts:
        tts = text

    return {
        "title": title,
        "description": desc,
        "tts_script": tts
    }