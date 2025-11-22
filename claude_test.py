# claude_test.py
import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-3-7-sonnet-latest"   # This is the correct Sonnet-4.x line

TEST_PROMPT = """
You are Leninware.

Write a 5-line Leninware analysis of this transcript fragment:

"Donald refused to denounce a fascist figure. Commentators framed it as cowardice."

Rules:
- Extremely provocative first line.
- Class-first, materialist analysis.
- No centrist framing.
- No soft language.
- End with: Real comrades like and subscribe.
"""

def test_claude():
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": TEST_PROMPT}]
        )
        print("\n=== CLAUDE RESPONSE ===\n")
        print(resp.content[0].text)
    except Exception as e:
        print("Claude error:", e)

if __name__ == "__main__":
    test_claude()