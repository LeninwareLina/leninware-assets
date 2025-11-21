from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

models_to_test = [
    "claude-3-opus-latest",
    "claude-3-5-sonnet-latest",
    "claude-3-5-haiku-latest",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]

print("\n=== Testing AVAILABLE models for this API key ===\n")

for m in models_to_test:
    try:
        print(f"Testing {m}...")
        resp = client.messages.create(
            model=m,
            max_tokens=5,
            messages=[{"role": "user", "content": "Test"}]
        )
        print(f"✔ AVAILABLE: {m}\n")
    except Exception as e:
        print(f"✘ NOT AVAILABLE: {m}")
        print(f"  Error: {e}\n")