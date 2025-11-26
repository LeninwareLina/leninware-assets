# image_prompt_builder.py

from typing import List
from safe_image_prompt_filter import apply_safe_substitutions


def build_image_prompts_from_commentary(commentary: str) -> List[str]:
    """
    Build a small set of image prompts based on the Leninware commentary.

    For now, keep it simple: 3-4 stylized prompts.
    """
    if not commentary or commentary.strip() == "":
        return []

    commentary = commentary.strip()

    base_prompts = [
        (
            "abstract symbolic imagery representing political tension, "
            "hierarchical power structures, dramatic lighting, red and black palette, "
            "dynamic composition, no real people"
        ),
        (
            "surreal metaphorical scene showing media influence and ideological conflict, "
            "geometric shapes and fractured light patterns, evoking systemic pressure and "
            "social struggle without literal violence"
        ),
        (
            "stylized representation of class contradictions and mass oppression, using "
            "oppressive shadows and bold color fields, evoking urgency without depicting "
            "specific events or individuals"
        ),
    ]

    # Run through the safe filter to avoid anything that trips safety systems
    safe_prompts = [apply_safe_substitutions(p) for p in base_prompts]

    return safe_prompts