# safe_image_prompt_filter.py

from pathlib import Path
from typing import List

RULES_PATH = Path("prompts/safe_substitution_rules.txt")


def _load_rules() -> List[tuple[str, str]]:
    """Load substitution rules from file, with debug logging."""
    if not RULES_PATH.exists():
        print(f"[prompt_filter] WARNING: Rules file missing → {RULES_PATH}")
        return []

    lines = RULES_PATH.read_text().splitlines()
    rules = []

    print(f"[prompt_filter] Loading rules from: {RULES_PATH}")

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if "=>" not in line:
            print(f"[prompt_filter] Skipping malformed rule: {raw}")
            continue

        before, after = line.split("=>", 1)
        before, after = before.strip(), after.strip()

        rules.append((before, after))
        print(f"[prompt_filter]   rule: '{before}' → '{after}'")

    if not rules:
        print("[prompt_filter] No valid rules found.")

    return rules


def apply_safe_substitutions(prompts: List[str]) -> List[str]:
    """Apply safe substitutions with verbose logging."""
    rules = _load_rules()

    if not rules:
        print("[prompt_filter] No rules applied (none loaded).")
        return prompts

    safe_prompts = []

    print(f"[prompt_filter] Applying {len(rules)} rules to {len(prompts)} prompts...")

    for i, p in enumerate(prompts, start=1):
        print(f"\n[prompt_filter] ---- Prompt {i} BEFORE ----")
        print(p)

        original = p
        for before, after in rules:
            if before in p:
                print(f"[prompt_filter]   Substituting '{before}' → '{after}'")
                p = p.replace(before, after)

        if p != original:
            print(f"[prompt_filter] ---- Prompt {i} AFTER ----")
            print(p)
        else:
            print(f"[prompt_filter] Prompt {i}: no substitutions needed.")

        safe_prompts.append(p)

    print("\n[prompt_filter] Substitution complete.\n")

    return safe_prompts