# https://copilot.microsoft.com/chats/dZs6u27tfmmjbUdQqTY79

import string
import re
from difflib import get_close_matches
from family import Family

def extract_families_from_request(
    request_string,
    last_to_firstnames,
    last_to_families,
    fuzzy_cutoff=0.90,
    use_fuzzy=False,
    debug=False,
):
    """
    Extracts families mentioned in a request string using:
    1. Last-name matching (exact + optional fuzzy)
    2. First-name disambiguation when multiple families share a last name
    3. Returns all matching families when ambiguity remains
    """

    # Normalize and strip punctuation
    raw = request_string
    req = request_string.lower()
    req = strip_possessives(req)
    req = req.translate(str.maketrans("", "", string.punctuation))
    tokens = req.split()


    if debug:
        print("\n=== extract_families_from_request ===")
        print(f"Raw request: {raw!r}")
        print(f"Normalized request: {req!r}")
        print(f"Tokens: {tokens}")
        print(f"Last-to-firstnames keys: {list(last_to_firstnames.keys())}")
        print(f"Fuzzy matching enabled: {use_fuzzy}")

    matched_families = []
    detected_last_names = set()

    # Step 1 — detect last names
    for last in last_to_firstnames.keys():
        last_lower = last.lower()

        # Exact token match
        if last_lower in tokens:
            detected_last_names.add(last)
            if debug:
                print(f"  Detected last name by token: {last!r}")
            continue

        # Optional fuzzy match
        if use_fuzzy:
            close = get_close_matches(last_lower, tokens, n=1, cutoff=fuzzy_cutoff)
            if close:
                detected_last_names.add(last)
                if debug:
                    print(f"  Detected last name by fuzzy match: {last!r} ~ {close[0]!r}")

    if debug:
        print(f"Detected last names: {detected_last_names}")

    # Step 2 — disambiguation logic
    for last in detected_last_names:
        families = last_to_families[last]

        if debug:
            print(f"\nProcessing last name: {last!r}")
            print(f"  Candidate families: {families}")
            print(f"  Possible first names: {last_to_firstnames[last]}")

        if len(families) == 1:
            matched_families.append(families[0])
            continue

        possible_firsts = last_to_firstnames[last]
        found_firsts = [first for first in possible_firsts if first.lower() in tokens]

        if len(found_firsts) == 1:
            first = found_firsts[0].lower()
            for fam in families:
                if fam.first_name.lower() == first:
                    matched_families.append(fam)
                    break
            continue

        if len(found_firsts) > 1:
            for fam in families:
                if fam.first_name in found_firsts:
                    matched_families.append(fam)
            continue

        matched_families.extend(families)

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


def strip_possessives(text: str) -> str:
    # Handles: Smith's, Adams’, Jones’s, Williams’
    return re.sub(r"(\w+)(['’]s|s['’])\b", r"\1", text)

def print_requests_map(requests_map: dict["Family", list["Family"]]) -> None:
    """
    Pretty-print the requests map in a clean, readable format.

    Example output:

    === REQUESTS MAP ===
    John Smith (part=0) -> Ava Jones, Paul Smith
    Big Family (part=1) -> <none>
    =====================
    """
    print("\n=== REQUESTS MAP ===")

    # Sort keys for stable, predictable output
    for fam in sorted(requests_map.keys(), key=lambda f: (f.last_name, f.first_name, f.part)):
        reqs = requests_map.get(fam, [])
        if reqs:
            req_str = ", ".join(
                f"{r.first_name} {r.last_name}" + (f" (part={r.part})" if r.part else "")
                for r in reqs
            )
        else:
            req_str = "<none>"

        # Include part only when non-zero
        part_str = f" (part={fam.part})" if fam.part else ""
        print(f"{fam.first_name} {fam.last_name}{part_str} -> {req_str}")

    print("====================\n")

