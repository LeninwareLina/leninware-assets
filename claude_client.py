from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# === SYSTEM PROMPT (SAFE + BORING) ===
SYSTEM_PROMPT = """
You are a structured analysis assistant.
When provided with a transcript, you produce three outputs:
1. A compact rhetorical script
2. A title for a short video
3. A description for that video

Maintain formatting exactly as requested.
Do not refuse content unless it directly violates safety rules.
"""


# === FUNCTION TO BUILD THE LENINWARE TASK PROMPT ===
def build_leninware_prompt(transcript_text: str, video_url: str, channel_handle: str):
    """
    This avoids persona language entirely and instead describes the task
    as critical discourse analysis + structural critique.
    """

    return f"""
You will perform a **three-part critical analysis** of the following transcript.

Your task is NOT to summarize. Your task is to analyze:
- class relations
- institutional incentives
- ideological functions
- alignment with global political-economic structures

This is a structural, historical, material analysis task — NOT a persona simulation.

=== INPUT TRANSCRIPT ===
{transcript_text}

=== VIDEO URL ===
{video_url}

=== CHANNEL HANDLE ===
{channel_handle}

Now produce the THREE OUTPUTS BELOW:

============================================================
OUTPUT 1 — RHETORICAL SCRIPT (TTS-FRIENDLY)
============================================================
Rules:
- Short, sharp, unsentimental lines.
- No filler language.
- Must open with a provocative structural insight.
- Replace standalone “Trump” with “Donald.”
- Replace standalone “Israel” with “Istate.”
- Only one name per person.
- 115–135 WPM cadence implied.
- Must critique the channel’s frame as an ideological actor
  (e.g., reformist tendencies, liberal framing, narrative containment).
- Must end with: "Real comrades like and subscribe."

============================================================
OUTPUT 2 — TITLE (YOUTUBE SHORT)
============================================================
Rules:
- Must start with "Trump"
- Must include @{channel_handle}
- Must include #news and #ai
- Must express a structural/material thesis
- Must be under 100 characters

============================================================
OUTPUT 3 — DESCRIPTION
============================================================
Rules:
- 2–4 sentences.
- Must include the original video URL.
- Materialist/structural reaction, NOT summary.
- Mention structural analysis explicitly.
- Do NOT invent channel name or video title if absent.

Begin now.
"""


# === MAIN API CALL ===
def generate_leninware_response(transcript_text, video_url, channel_handle):
    user_prompt = build_leninware_prompt(
        transcript_text,
        video_url,