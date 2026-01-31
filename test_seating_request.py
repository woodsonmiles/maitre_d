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

    req = "Please seat us with the Smiths"
    result = extract_families_from_request(req, last_to_firstnames, last_to_families)

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
    result = extract_families_from_request(req, last_to_firstnames, last_to_families)

    assert result == [jones]

