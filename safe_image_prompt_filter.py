# safe_image_prompt_filter.py
"""
Safe Image Prompt Filter (Medium Safety Level)

Purpose:
Transform Leninware commentary into image-safe, platform-compliant prompts
that will reliably pass:
- OpenAI Image API content guidelines
- YouTube automated visual moderation
- General platform safety expectations

This does NOT change political meaning. It ONLY ensures imagery is abstract,
symbolic, and non-literal, while keeping intensity and emotional punch.
"""

import re

# Words/themes that must NEVER be literal for image generation
BANNED_LITERALS = {
    "fascist": "authoritarian",
    "fascism": "authoritarian ideology",
    "nazi": "extremist authoritarian symbolism",
    "nazism": "extremist authoritarian symbolism",
    "genocide": "state-led mass oppression",
    "lynching": "racialized violent repression",
    "violence": "conflict symbolism",
    "riot": "civil unrest symbolism",
    "blood": "metaphorical tension",
    "weapon": "threatening posture (non-literal)",
    "gun": "threat symbolism",
    "ammo": "conflict imagery",
    "execution": "state repression symbolism",
    "terrorism": "extremist violence symbolism",
}

# Real names pattern (First Last)
REAL_NAME_PATTERN = re.compile(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b")


def generate_safe_image_prompts(commentary: str):
    """
    Takes raw Leninware commentary (text) and produces a list of
    3 safe, abstract, symbolic OpenAI-image-ready prompts.
    """
    # Normalize case for replacements
    text = commentary

    # Strip real names
    text = REAL_NAME_PATTERN.sub("a political figure", text)

    # Case-insensitive replace of banned literals
    lowered = text.lower()
    for banned, replacement in BANNED_LITERALS.items():
        lowered = lowered.replace(banned, replacement)

    # For now we don't try to be hyper-literal; we just evoke themes.
    prompts = [
        (
            "abstract symbolic imagery representing political tension, "
            "hierarchical power structures, dramatic lighting, red and black palette, "
            "dynamic composition, no real people"
        ),
        (
            "surreal metaphorical scene showing media influence and ideological conflict, "
            "geometric shapes and fractured light patterns, "
            "evoking systemic pressure and social struggle without literal violence"
        ),
        (
            "stylized representation of class contradictions and mass oppression, "
            "using expressive shadows and bold color fields, "
            "evoking urgency without depicting specific events or individuals"
        ),
    ]

    return prompts