# safe_image_prompt_filter.py

from pathlib import Path
from typing import List

RULES_PATH = Path("prompts/safe_substitution_rules.txt")

def _load_rules() -> List[tuple[str, str]]:
    if not RULES_PATH.exists():
        return []
    rules = []
    for line in RULES_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=>" not in line:
            continue
        before, after = line.split("=>", 1)
        rules.append((before.strip(), after.strip()))
    return rules

def apply_safe_substitutions(prompts: List[str]) -> List[str]:
    rules = _load_rules()
    if not rules:
        return prompts
    safe = []
    for p in prompts:
        for before, after in rules:
            p = p.replace(before, after)
        safe.append(p)
    return safe