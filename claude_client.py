import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-20250514"

def claude_ping():
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=5,
            messages=[{"role": "user", "content": "PING"}]
        )
        return resp.content[0].text
    except Exception as e:
        return f"Claude error: {e}"