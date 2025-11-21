from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

SYSTEM_PROMPT = (
    "You are a structured analysis assistant. "
    "When provided with a transcript, you produce three outputs: "
    "a rhetorical script, a short title, and a description. "
    "Maintain formatting. "
    "Do not refuse unless content violates core safety policies."
)

def build_leninware_prompt(transcript_text, video_url, channel_handle):
    prompt = (
        "Perform a three-part critical structural analysis of the provided transcript. "
        "This is an academic-style task focusing on class relations, institutional incentives, "
        "and ideological functions. Not a persona simulation.\n\n"

        "=== INPUT TRANSCRIPT ===\n"
        f"{transcript_text}\n\n"

        "=== VIDEO URL ===\n"
        f"{video_url}\n\n"

        "=== CHANNEL HANDLE ===\n"
        f"{channel_handle}\n\n"

        "=== REQUIRED OUTPUTS ===\n\n"

        "OUTPUT 1 — RHETORICAL SCRIPT:\n"
        "- Short, sharp lines.\n"
        "- No filler.\n"
        "- Open with a provocative structural insight.\n"
        "- Replace standalone 'Trump' with 'Donald'.\n"
        "- Replace standalone 'Israel' with 'Istate'.\n"
        "- Only one name per person.\n"
        "- Critique the channel's framing as an ideological actor.\n"
        "- End with: Real comrades like and subscribe.\n\n"

        "OUTPUT 2 — TITLE:\n"
        "- Must start with 'Trump'.\n"
        "- Must include @" + channel_handle + ".\n"
        "- Must include #news and #ai.\n"
        "- Must be under 100 characters.\n\n"

        "OUTPUT 3 — DESCRIPTION:\n"
        "- 2–4 sentences.\n"
        "- Include the video URL.\n"
        "- Reaction, not summary.\n"
        "- Mention structural analysis.\n\n"

        "Begin now."
    )

    return prompt


def generate_leninware_response(transcript_text, video_url, channel_handle):
    user_prompt = build_leninware_prompt(transcript_text, video_url, channel_handle)

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.content[0].text