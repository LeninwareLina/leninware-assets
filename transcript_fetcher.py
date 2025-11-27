import os
import requests

TRANSCRIPT_API_URL = "https://transcriptapi.com/api/v1/transcript"

def fetch_transcript(video_url):
    api_key = os.getenv("TRANSCRIPT_API_KEY")
    if not api_key:
        print("[worker] ERROR: TRANSCRIPT_API_KEY missing")
        return None

    try:
        response = requests.post(
            TRANSCRIPT_API_URL,
            json={"url": video_url},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("transcript", None)

        print(f"[worker] Transcript error: {response.status_code} - {response.text}")
        return None

    except Exception as e:
        print(f"[worker] Transcript request FAILED: {e}")
        return None