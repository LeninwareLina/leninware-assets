# claude_sonnet4_test.py
import os
import anthropic

# Load your environment API key (Railway will insert it automatically)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-20250514"

TEST_TRANSCRIPT = """
Donald refused to denounce a fascist figure, and commentators framed it as simple cowardice.
Provide a Leninware-style reaction to this fragment.
"""

SYSTEM = """
You are LENINWARE — a militant, structural, anti-liberal analytic engine.
Your job is to produce ONE output only:

TTS_SCRIPT:
A 12–18 line Leninware-style monologue that:
- opens with an extremely provocative first line
- is short, sharp, unsentimental
- replaces “Trump” with “Donald”
- replaces “Israel” with “Istate”
- directly critiques the YouTube channel's ideological function
- avoids all liberal framing
- ends with: Real comrades like and subscribe.
"""

USER = f"""
Transcript fragment:
{TEST_TRANSCRIPT}

Respond ONLY with the TTS_SCRIPT. No labels, no title, no description, no explanation.
"""

def test_claude():
    print("\n=== Testing Claude Sonnet 4 ===\n")
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=SYSTEM,
            messages=[{"role": "user", "content": USER}]
        )
        print(resp.content[0].text)
    except Exception as e:
        print("\nClaude ERROR:\n", e)

if __name__ == "__main__":
    test_claude()