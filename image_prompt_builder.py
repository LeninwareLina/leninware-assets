# image_prompt_builder.py
from typing import List
from safe_image_prompt_filter import generate_safe_image_prompts


def build_image_prompts_from_commentary(commentary: str) -> List[str]:
    """
    Given Leninware commentary text, return a small collection of safe,
    abstract prompts for AI image generation.
    """
    return generate_safe_image_prompts(commentary)