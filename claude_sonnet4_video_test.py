# claude_sonnet4_video_test.py
import os
import requests
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")

MODEL = "claude-sonnet-4-20250514"

SYSTEM = """
You are LENINWARE — a militant, structural, anti-liberal analytic engine.

Your output must be ONE block only:

TTS_SCRIPT:
- 12–18 lines
- extremely provocative first line
- punchy, unsentimental
- replace 'Trump' with 'Donald'
- replace 'Israel' with 'Istate'
- identify class forces, structural incentives, ideological function, and imperial order
- attack liberal framing, reformism, and media laundering
- end with: Real comrades like and subscribe.

NO labels, NO explanations.
"""

def get_transcript(video_url):
    try:
        resp = requests.get(
            "https://transcriptapi.com/api/v2/youtube/transcript",
            params={"video_url": video_url, "format": "text"},
            headers={"Authorization": f"Bearer {TRANSCRIPT_API_KEY}"}
        )
        if resp.status_code != 200:
            return None, f"TranscriptAPI error: {resp.text}"
        return resp.text, None
    except Exception as e:
        return None, f"TranscriptAPI exception: {e}"

def generate_leninware(transcript):
    USER = f"Transcript:\n{transcript}\n\nGenerate the TTS_SCRIPT only."

    try:
        resp = client.messages.create(
            model=MODEL,
            system=SYSTEM,
            max_tokens=900,
            messages=[{"role": "user", "content": USER}]
        )
        return resp.content[0].text
    except Exception as e:
        return f"Claude error: {e}"

if __name__ == "__main__":
    print("Paste a YouTube URL to test Leninware Sonnet-4:")
    url = input("> ").strip()

    transcript, err = get_transcript(url)
    if err:
        print("\n--- TRANSCRIPT ERROR ---")
        print(err)
        exit()

    print("\n--- TRANSCRIPT FETCHED ---")
    print("(length:", len(transcript), "characters )")

    print("\n--- LENINWARE OUTPUT ---\n")
    print(generate_leninware(transcript))