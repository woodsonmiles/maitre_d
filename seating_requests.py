# https://copilot.microsoft.com/chats/dZs6u27tfmmjbUdQqTY79

import string
from difflib import get_close_matches

def extract_families_from_request(
    request_string,
    last_to_firstnames,
    last_to_families,
    fuzzy_cutoff=0.8,
    debug=False,
):
    """
    Extracts families mentioned in a request string using:
    1. Last-name matching (exact + fuzzy)
    2. First-name disambiguation when multiple families share a last name
    3. Returns all matching families when ambiguity remains

    Parameters:
        request_string (str)
        last_to_firstnames (dict[str, list[str]])
        last_to_families (dict[str, list[Family]])
        fuzzy_cutoff (float): threshold for fuzzy last-name matching
        debug (bool): when True, prints details of the extraction process

    Returns:
        list[Family]
    """

    # Normalize and strip punctuation
    raw = request_string
    req = request_string.lower()
    req = req.translate(str.maketrans("", "", string.punctuation))
    tokens = req.split()

    if debug:
        print("\n=== extract_families_from_request ===")
        print(f"Raw request: {raw!r}")
        print(f"Normalized request: {req!r}")
        print(f"Tokens: {tokens}")
        print(f"Last-to-firstnames keys: {list(last_to_firstnames.keys())}")

    matched_families = []

    # Step 1 — detect last names
    detected_last_names = set()

    for last in last_to_firstnames.keys():
        last_lower = last.lower()

        # Exact substring match in full request (robust to spacing)
        if last_lower in req:
            detected_last_names.add(last)
            if debug:
                print(f"  Detected last name by substring: {last!r}")
            continue

        # Exact token match
        if last_lower in tokens:
            detected_last_names.add(last)
            if debug:
                print(f"  Detected last name by token: {last!r}")
            continue

        # Fuzzy match against individual tokens
        close = get_close_matches(last_lower, tokens, n=1, cutoff=fuzzy_cutoff)
        if close:
            detected_last_names.add(last)
            if debug:
                print(f"  Detected last name by fuzzy match: {last!r} ~ {close[0]!r}")

    if debug:
        print(f"Detected last names: {detected_last_names}")

    # Step 2 — for each detected last name, disambiguate using first names
    for last in detected_last_names:
        families = last_to_families[last]

        if debug:
            print(f"\nProcessing last name: {last!r}")
            print(f"  Candidate families: {families}")
            print(f"  Possible first names: {last_to_firstnames[last]}")

        # If only one family has this last name → done
        if len(families) == 1:
            matched_families.append(families[0])
            if debug:
                print(f"  Only one family with last name {last!r}: {families[0]}")
            continue

        possible_firsts = last_to_firstnames[last]
        found_firsts = [
            first for first in possible_firsts
            if first.lower() in tokens
        ]

        if debug:
            print(f"  Found first names in request: {found_firsts}")

        # If exactly one first name matches → disambiguated
        if len(found_firsts) == 1:
            first = found_firsts[0].lower()
            chosen = None
            for fam in families:
                if fam.first_name.lower() == first:
                    matched_families.append(fam)
                    chosen = fam
                    break
            if debug:
                print(f"  Disambiguated by first name {found_firsts[0]!r}: {chosen}")
            continue

        # If multiple first names match → return all matching families
        if len(found_firsts) > 1:
            for fam in families:
                if fam.first_name in found_firsts:
                    matched_families.append(fam)
            if debug:
                print(f"  Multiple first names matched; returning all matching families: {matched_families}")
            continue

        # If no first names match → ambiguous → return all families
        matched_families.extend(families)
        if debug:
            print(f"  No first-name disambiguation; returning all families: {families}")

    # Deduplicate while preserving order
    seen = set()
    result = []
    for fam in matched_families:
        if fam not in seen:
            seen.add(fam)
            result.append(fam)

    if debug:
        print(f"\nFinal matched families (deduped): {result}")
        print("=== end extract_families_from_request ===\n")

    return result
