import pytest
from family import Family, Guest, Meal

def make_family(email, phone, address):
    # minimal Family factory for testing
    return Family(
        email=email,
        phone=phone,
        address=address,
        requests="",
        guests=[Guest("Test", "User", Meal.Chicken, "", 30)]
    )

def test_unique_families_removes_duplicates_by_phone():
    fam1 = make_family("a@example.com", "123", "Addr1")
    fam2 = make_family("b@example.com", "123", "Addr2")  # duplicate phone
    families = {fam1, fam2}

    unique = Family.unique_families(families)
    assert len(unique) == 1
    assert any(f.phone == "123" for f in unique)

def test_unique_families_removes_duplicates_by_address():
    fam1 = make_family("a@example.com", "111", "SameAddr")
    fam2 = make_family("b@example.com", "222", "SameAddr")  # duplicate address
    families = {fam1, fam2}

    unique = Family.unique_families(families)
    assert len(unique) == 1
    assert any(f.address == "SameAddr" for f in unique)

def test_unique_families_keeps_unique_entries():
    fam1 = make_family("a@example.com", "111", "Addr1")
    fam2 = make_family("b@example.com", "222", "Addr2")
    families = {fam1, fam2}

    unique = Family.unique_families(families)
    assert len(unique) == 2
    assert fam1 in unique and fam2 in unique

def test_unique_families_empty_set():
    families = set()
    unique = Family.unique_families(families)
    assert unique == set()

