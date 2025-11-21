import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

TRANSCRIPT_API_KEY = os.getenv("TRANSCRIPT_API_KEY")

BASE_URL = "https://api.transcriptapi.com/api/v1/transcript"

@app.route("/")
def home():
    return "Leninware Transcript Proxy (Railway) is running."

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/youtube/<video_id>")
def youtube(video_id):
    if not TRANSCRIPT_API_KEY:
        return jsonify({"error": "Missing TRANSCRIPT_API_KEY"}), 500

    url = f"{BASE_URL}/{video_id}"
    headers = {"X-Api-Key": TRANSCRIPT_API_KEY}

    try:
        r = requests.get(url, headers=headers, timeout=20)
        try:
            return jsonify(r.json())
        except Exception:
            return jsonify({"error": "Non-JSON returned", "raw": r.text}), 500

    except Exception as e:
        return jsonify({"error": "Proxy request failed", "details": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)