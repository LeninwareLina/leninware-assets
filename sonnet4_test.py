import anthropic

client = anthropic.Anthropic(api_key="YOUR_API_KEY_HERE")

MODEL = "claude-sonnet-4-20250514"

print(f"Testing model: {MODEL}")

try:
    response = client.messages.create(
        model=MODEL,
        max_tokens=20,
        messages=[
            {"role": "user", "content": "Say PING"}
        ]
    )
    print("SUCCESS:", response.content[0].text)

except Exception as e:
    print("ERROR:", e)