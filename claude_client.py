# claude_client.py
import os
from anthropic import Anthropic

MODEL_NAME = "claude-3-5-sonnet-latest"

def claude_ping():
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise RuntimeError("CLAUDE_API_KEY missing")

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=20,
        messages=[
            {"role": "user", "content": "Reply with: PONG"}
        ]
    )

    return response.content[0].text.strip()