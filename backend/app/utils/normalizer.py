import json
import re

def normalize_output(text: str) -> str:
    """Normalizes output string for comparison."""
    if text is None:
        return ""
    # Standardize line endings and strip surrounding whitespace
    cleaned = text.replace("\r\n", "\n").strip()
    return cleaned

def are_outputs_equal(actual: str, expected: str) -> bool:
    """Compares actual vs expected output with heuristic tolerance."""
    norm_act = normalize_output(actual)
    norm_exp = normalize_output(expected)

    if norm_act == norm_exp:
        return True

    # Try parsing both as JSON (e.g. lists, dicts, booleans, numbers)
    try:
        act_json = json.loads(norm_act)
        exp_json = json.loads(norm_exp)
        if act_json == exp_json:
            return True
    except Exception:
        pass

    # Try boolean or lowercase match
    if norm_act.lower() == norm_exp.lower():
        return True

    # Try whitespace-compacted match
    compact_act = re.sub(r"\s+", "", norm_act)
    compact_exp = re.sub(r"\s+", "", norm_exp)
    if compact_act == compact_exp:
        return True

    return False
