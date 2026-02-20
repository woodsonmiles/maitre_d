import pytest

from seating_requests import extract_families_from_request
from family import Family, Guest, Meal
from datetime import datetime

def make_family(first_name, last_name, email=""):
    if not email:
        email = f"{first_name}.{last_name}"
    # minimal Family factory for testing
    return Family(
        email=email,
        phone='1231231233',
        address="",
        requests="",
        submission=datetime.now(),
        guests=[Guest(first_name, last_name, Meal.Chicken, "", 30)]
    )

@pytest.fixture
def sample_data():
    # Families with same last name
    smith1 = make_family("John", "Smith")
    smith2 = make_family("Paul", "Smith")

    # Unique last name
    jones = make_family("Ava", "Jones")

    last_to_firstnames = {
        "Smith": ["John", "Paul"],
        "Jones": ["Ava"],
    }

    last_to_families = {
        "Smith": [smith1, smith2],
        "Jones": [jones],
    }

    return last_to_firstnames, last_to_families, smith1, smith2, jones


def test_unique_last_name(sample_data):
    """If only one family has a last name, it should match directly."""
    last_to_firstnames, last_to_families, _, _, jones = sample_data

    req = "We want to sit with the Jones family"
    result = extract_families_from_request(req, last_to_firstnames, last_to_families)

    assert result == [jones]


def test_disambiguate_by_first_name(sample_data):
    """If multiple families share a last name, first names should disambiguate."""
    last_to_firstnames, last_to_families, smith1, smith2, _ = sample_data

    req = "Please seat us with John Smith"
    result = extract_families_from_request(req, last_to_firstnames, last_to_families, debug=True)

    assert result == [smith1]


def test_multiple_first_names_match(sample_data):
    """If multiple first names appear, return all matching families."""
    last_to_firstnames, last_to_families, smith1, smith2, _ = sample_data

    req = "We want to sit with John and Paul Smith"
    result = extract_families_from_request(req, last_to_firstnames, last_to_families, debug=True)

    assert set(result) == {smith1, smith2}


def test_ambiguous_last_name_no_first_names(sample_data):
    """If no first names appear, return all families with that last name."""
    last_to_firstnames, last_to_families, smith1, smith2, _ = sample_data

    """Pluralizing requires fuzzy right now"""
    req = "Please seat us with the Smiths"
    result = extract_families_from_request(req, last_to_firstnames, last_to_families, use_fuzzy=True)

    assert set(result) == {smith1, smith2}


def test_case_insensitive_matching(sample_data):
    """Matching should be case-insensitive for both first and last names."""
    last_to_firstnames, last_to_families, smith1, _, _ = sample_data

    req = "PLEASE SEAT US WITH JOHN SMITH"
    result = extract_families_from_request(req, last_to_firstnames, last_to_families, debug=True)

    assert result == [smith1]


def test_fuzzy_last_name_matching(sample_data):
    """Fuzzy matching should catch misspelled last names."""
    last_to_firstnames, last_to_families, _, _, jones = sample_data

    req = "We want to sit with the Joness family"  # misspelled
    result = extract_families_from_request(req, last_to_firstnames, last_to_families, use_fuzzy=True)

    assert result == [jones]

def test_extract_request_does_not_match_substrings_like_le_multiple_strings():
    """
    Families with short last names like 'Le' must not be matched when their
    name appears only as a substring inside other words. This test checks
    multiple request strings to ensure robustness.
    """

    # The family we want to ensure is NOT matched
    le_family = make_family("Alex", "Le")

    # Other families that *should* be matched
    andy = make_family("Andy", "Kazcka")
    brielle = make_family("Brielle", "Kazcka")
    weiler = make_family("Sam", "Weiler")
    teach = make_family("Tom", "Teach")

    families = [le_family, andy, brielle, weiler, teach]

    # Build lookup maps
    last_to_first = Family.last_to_firstnames(families)
    last_to_family = Family.last_to_family(families)

    request_strings = [
        "Please sit with Andy Kazcka and Brielle Kazcka",
        "Would like to sit next to Weiler and Teach families",
    ]

    for req in request_strings:
        matched = extract_families_from_request(
            request_string=req,
            last_to_firstnames=last_to_first,
            last_to_families=last_to_family,
        )

        # The Le family must NOT appear in the results
        assert le_family not in matched, f"'Le' incorrectly matched in: {req}"


# Test stripping posessive

def test_possessive_last_name_basic():
    smith = make_family("John", "Smith")

    last_to_first = {"Smith": ["John"]}
    last_to_families = {"Smith": [smith]}

    req = "Please seat us near Smith's family."

    result = extract_families_from_request(
        req, last_to_first, last_to_families, use_fuzzy=False, debug=True
    )

    assert result == [smith]

def test_possessive_mixed_case():
    smith = make_family("John", "Smith")

    last_to_first = {"Smith": ["John"]}
    last_to_families = {"Smith": [smith]}

    req = "Please seat us with SMITH’S group."

    result = extract_families_from_request(
        req, last_to_first, last_to_families, use_fuzzy=False
    )

    assert result == [smith]


def test_non_possessive_words_unchanged():
    smith = make_family("John", "Smith")

    last_to_first = {"Smith": ["John"]}
    last_to_families = {"Smith": [smith]}

    req = "Please seat us with the Smith family."

    result = extract_families_from_request(
        req, last_to_first, last_to_families, use_fuzzy=False
    )

    assert result == [smith]

def test_plural_friends_does_not_match_friend_last_name():
    friend = make_family("Damian", "Friend")

    last_to_first = {"Friend": ["Damian"]}
    last_to_families = {"Friend": [friend]}

    req = "Please seat us with our friends the Smiths."

    result = extract_families_from_request(
        req, last_to_first, last_to_families, use_fuzzy=False
    )

    assert result == []  # should NOT match "Friend"


def test_possessive_of_friend_matches_friend():
    friend = make_family("Damian", "Friend")

    last_to_first = {"Friend": ["Damian"]}
    last_to_families = {"Friend": [friend]}

    req = "Please seat us with Friend's family."

    result = extract_families_from_request(
        req, last_to_first, last_to_families, use_fuzzy=False
    )

    assert result == [friend]

def test_plural_last_name_not_stripped():
    jones = make_family("John", "Jones")

    last_to_first = {"Jones": ["John"]}
    last_to_families = {"Jones": [jones]}

    req = "Please seat us with Jones."

    result = extract_families_from_request(
        req, last_to_first, last_to_families, use_fuzzy=False, debug=True
    )
    assert result == [jones]

