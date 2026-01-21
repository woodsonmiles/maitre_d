# https://copilot.microsoft.com/chats/dZs6u27tfmmjbUdQqTY79
import re
from difflib import get_close_matches

def extract_last_names_from_requests(families, guest_last_names, cutoff=0.75):
    """
    families: list of objects with a .requests field (string)
    guest_last_names: list of valid last names (strings)
    cutoff: fuzzy match threshold (0–1)
    
    Returns: dict { family_object: [matched_last_names] }
    """

    # Normalize guest last names for matching
    guest_last_names_lower = [ln.lower() for ln in guest_last_names]

    result = {}

    for family in families:
        text = family.requests or ""

        # Extract capitalized words (potential names)
        tokens = re.findall(r"[A-Z][a-zA-Z]+", text)

        matched = []

        for token in tokens:
            token_lower = token.lower()

            # Exact match
            if token_lower in guest_last_names_lower:
                idx = guest_last_names_lower.index(token_lower)
                matched.append(guest_last_names[idx])
                continue

            # Fuzzy match
            close = get_close_matches(token_lower, guest_last_names_lower, n=1, cutoff=cutoff)
            if close:
                idx = guest_last_names_lower.index(close[0])
                matched.append(guest_last_names[idx])

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for ln in matched:
            if ln.lower() not in seen:
                seen.add(ln.lower())
                unique.append(ln)

        result[family] = unique

    return result
