def generate_leninware_commentary(transcript: str) -> str:
    """
    Sends transcript to GPT-4.1 using your Leninware system prompt.

    Returns: commentary string (whatever 4.1 outputs).
    """

    # Guard against empty / missing transcripts
    if not transcript or transcript.strip() == "":
        return "NO TRANSCRIPT PROVIDED."

    require_env("OPENAI_API_KEY", OPENAI_API_KEY)
    client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = load_leninware_system_prompt().strip()

    user_content = (
        "You will receive a structured input.\n"
        "Use ONLY the text inside the TRANSCRIPT block.\n"
        "Ignore any logs, errors, stack traces, or system messages.\n\n"
        "TRANSCRIPT:\n"
        "<<<BEGIN_TRANSCRIPT>>>\n"
        f"{transcript}\n"
        "<<<END_TRANSCRIPT>>>"
    )

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_content,
            },
        ],
        max_tokens=900,
        temperature=0.8,
    )

    return resp.choices[0].message.content.strip()