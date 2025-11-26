# safe_image_prompt_filter.py

from pathlib import Path

RULES_PATH = Path("prompts/safe_substitution_rules.txt")


def _load_rules():
    """
    Load simple substitution rules from prompts/safe_substitution_rules.txt

    Format per line:
    bad_phrase => safe_phrase
    """
    rules = []
    if not RULES_PATH.exists():
        return rules

    for line in RULES_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=>" not in line:
            continue
        bad, safe = [part.strip() for part in line.split("=>", 1)]
        if bad and safe:
            rules.append((bad, safe))
    return rules


_RULES = _load_rules()


def apply_safe_substitutions(text: str) -> str:
    """
    Apply substitution rules to prompts to reduce safety triggers.
    """
    if not text or not _RULES:
        return text

    out = text
    for bad, safe in _RULES:
        out = out.replace(bad, safe)
    return out