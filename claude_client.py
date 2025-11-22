# claude_client.py
import asyncio
from anthropic import AsyncAnthropic

# Keep your full Leninware system prompt exactly as it already is
from leninware_system_prompt import LENINWARE_SYSTEM_PROMPT


async def run_claude(transcript: str, api_key: str) -> str:
    client = AsyncAnthropic(api_key=api_key)

    user_prompt = f"""
Apply Leninware Mode to this transcript and generate:
TITLE
DESCRIPTION
TTS_SCRIPT

Transcript:
{transcript}
"""

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",   # <<<<<< EXACT MODEL ID YOU WANT TO TRY
        max_tokens=1800,
        system=LENINWARE_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": user_prompt}]
            }
        ]
    )

    return response.content[0].text