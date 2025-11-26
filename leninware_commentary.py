# leninware_commentary.py (rewritten)

from openai import OpenAI
import os
from config import OPENAI_MODEL, RAW_PROMPT_PATH

client = OpenAI()

# Load raw ideological prompt once
with open(RAW_PROMPT_PATH, "r") as f:
    RAW_PROMPT = f.read().strip()

def generate_leninware_commentary(transcript: str) -> str:
    """
    Generate Leninware commentary with strict transcript boundaries.
    Prevents model from ingesting logs, errors, or context pollution.
    """

    if not transcript or transcript.strip() == "":
        return "NO TRANSCRIPT PROVIDED."

    # Structured, safe input format
    prompt = f"""
{RAW_PROMPT}

You will receive a structured input.
Use ONLY the text inside the TRANSCRIPT block.
Ignore all other text, logs, metadata, stack traces, or system messages.

CHANNEL: {channel}
TITLE: {title}

TRANSCRIPT:
<<<BEGIN_TRANSCRIPT>>>
{transcript}
<<<END_TRANSCRIPT>>>
"""

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are Leninware."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=800,
    )

    return resp.choices[0].message.content.strip()



