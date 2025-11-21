# claude_client.py
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# The model your account supports
MODEL = "claude-3-haiku-20240307"

def build_leninware_prompt(transcript: str, url: str, channel: str) -> str:
    return f"""
You are producing a materialist, anti-liberal structural analysis of a YouTube political clip.

You must output THREE JSON fields exactly:
- "tts"
- "title"
- "description"

The transcript of the video is below:
---
{transcript}
---

Use the following rules when generating the output:

1. The "tts" output must:
   - Be sharp, punchy, unsentimental.
   - Avoid filler, avoid soft liberal framing.
   - Critique the CHANNEL itself ({channel}) for reformism, liberal framing, institutional capture, or ideological drift.
   - End with: "Real comrades like and subscribe."
   - Use only one name per person, no first + last.

2. The "title" output must:
   - Be under 100 characters.
   - Start with "Trump"
   - Include "@{channel}"
   - Include #news and #ai
   - Express a class-first or anti-imperialist idea.

3. The "description" must:
   - Be 2–4 sentences.
   - Reference the URL: {url}
   - Mention structural analysis.
   - Not hallucinate video titles.

Return ONLY valid JSON. No extra text.
    """

def generate_leninware_response(transcript: str, url: str, channel: str) -> dict:
    prompt = build_leninware_prompt(transcript, url, channel)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract text from Claude
    raw = response.content[0].text

    import json
    try:
        return json.loads(raw)
    except Exception:
        return {
            "tts": "Error: Invalid model output.",
            "title": "Error",
            "description": "The model returned invalid JSON."
        }