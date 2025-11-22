import os
import requests
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-20250514"
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")

def get_transcript(video_url: str):
    endpoint = "https://transcriptapi.com/api/v2/youtube/transcript"
    headers = {"Authorization": f"Bearer {TRANSCRIPT_API_KEY}"}
    params = {"video_url": video_url, "format": "text"}

    r = requests.get(endpoint, headers=headers, params=params)
    r.raise_for_status()
    return r.text

LENINWARE_TTS_PROMPT = {
    "role": "system",
    "content": [
        {
            "type": "text",
            "text": "SYSTEM: Leninware TTS Mode Active.\nProduce 1 ultra-provocative TTS script only.\nShort, punchy, ruthless, anti-imperialist, class-first.\nNo moralizing. No both-sides. No softness.\nReplace 'Trump' with 'Donald'. Replace 'Israel' with 'Istate'."
        }
    ]
}

if __name__ == "__main__":
    url = "https://youtu.be/QrrhLB-JVno?si=_6927fgOJy0-7H1c"

    print("Fetching transcript...")
    transcript = get_transcript(url)
    print("Transcript retrieved, sending to Claude Sonnet-4...\n")

    msg = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=LENINWARE_TTS_PROMPT["content"][0]["text"],
        messages=[{
            "role": "user",
            "content": transcript
        }]
    )

    print("==== LENINWARE SONNET-4 OUTPUT ====\n")
    print(msg.content[0].text)