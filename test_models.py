from anthropic import Anthropic

API_KEY = "REPLACE_WITH_YOUR_REAL_KEY"

client = Anthropic(api_key=API_KEY)

models_to_test = [
    "claude-3-opus-latest",
    "claude-3-5-sonnet-latest",
    "claude-3-5-haiku-latest",
]

print("\n=== Testing models ===\n")

for m in models_to_test:
    try:
        print(f"Testing {m}...")
        resp = client.messages.create(
            model=m,
            max_tokens=5,
            messages=[{"role": "user", "content": "Hello"}]
        )
        print(f"✔ AVAILABLE: {m}\n")
    except Exception as e:
        print(f"✘ NOT AVAILABLE: {m}")
        print(f"  Error: {e}\n")