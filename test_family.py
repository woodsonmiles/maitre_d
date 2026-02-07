import pytest
from family import Family, Guest, Meal
from datetime import datetime

def make_family(email, phone='', address='', part=0):
    # minimal Family factory for testing
    return Family(
        email=email,
        phone=phone,
        address=address,
        requests="",
        submission=datetime.now(),
        part=part,
        guests=[Guest("Test", "User", Meal.Chicken, "", 30)]
    )

def test_unique_families_removes_duplicates_by_phone():
    fam1 = make_family("a@example.com", "123", "Addr1")
    fam2 = make_family("b@example.com", "123", "Addr2")  # duplicate phone
    families = {fam1, fam2}

    unique = Family.unique(families)
    assert len(unique) == 1
    assert any(f.phone == "123" for f in unique)

def test_unique_families_removes_duplicates_by_address():
    fam1 = make_family("a@example.com", "111", "SameAddr")
    fam2 = make_family("b@example.com", "222", "SameAddr")  # duplicate address
    families = {fam1, fam2}

    unique = Family.unique(families)
    assert len(unique) == 1
    assert any(f.address == "SameAddr" for f in unique)

def test_unique_families_keeps_unique_entries():
    fam1 = make_family("a@example.com", "111", "Addr1")
    fam2 = make_family("b@example.com", "222", "Addr2")
    families = {fam1, fam2}

    unique = Family.unique(families)
    assert len(unique) == 2
    assert fam1 in unique and fam2 in unique

def test_unique_families_empty_set():
    families = set()
    unique = Family.unique(families)
    assert unique == set()
import pytest
from family import Family, Guest, Meal
from datetime import datetime




# ---------------------------------------------------------
# Equality tests
# ---------------------------------------------------------

def test_equal_families_same_email_and_part():
    f1 = make_family("a@example.com", part=0)
    f2 = make_family("a@example.com", part=0)

    assert f1 == f2
    assert not (f1 != f2)


def test_not_equal_when_part_differs():
    f1 = make_family("a@example.com", part=0)
    f2 = make_family("a@example.com", part=1)

    assert f1 != f2
    assert not (f1 == f2)


def test_not_equal_when_email_differs():
    f1 = make_family("a@example.com", part=0)
    f2 = make_family("b@example.com", part=0)

    assert f1 != f2


def test_not_equal_to_non_family():
    f1 = make_family("a@example.com", part=0)
    assert f1 != "not a family"


# ---------------------------------------------------------
# Hashing tests
# ---------------------------------------------------------

def test_hash_same_for_equal_families():
    f1 = make_family("a@example.com", part=0)
    f2 = make_family("a@example.com", part=0)

    assert hash(f1) == hash(f2)


def test_hash_differs_when_part_differs():
    f1 = make_family("a@example.com", part=0)
    f2 = make_family("a@example.com", part=1)

    assert hash(f1) != hash(f2)


def test_hash_differs_when_email_differs():
    f1 = make_family("a@example.com", part=0)
    f2 = make_family("b@example.com", part=0)

    assert hash(f1) != hash(f2)


# ---------------------------------------------------------
# Set and dict behavior
# ---------------------------------------------------------

def test_set_treats_split_families_as_distinct():
    f0 = make_family("big@example.com", part=0)
    f1 = make_family("big@example.com", part=1)

    s = {f0, f1}
    assert len(s) == 2
    assert f0 in s
    assert f1 in s


def test_dict_keys_treat_split_families_as_distinct():
    f0 = make_family("big@example.com", part=0)
    f1 = make_family("big@example.com", part=1)

    d = {f0: "first", f1: "second"}

    assert d[f0] == "first"
    assert d[f1] == "second"
    assert len(d) == 2


def test_part_zero_behaves_like_original_identity():
    """Families with part=0 should behave exactly like the old identity model."""
    f1 = make_family("x@example.com", part=0)
    f2 = make_family("x@example.com", part=0)

    assert f1 == f2
    assert hash(f1) == hash(f2)


# ---------------------------------------------------------
# Repr tests (optional but helpful)
# ---------------------------------------------------------

def test_repr_includes_part_only_when_nonzero():
    f0 = make_family("a@example.com", part=0)
    f1 = make_family("a@example.com", part=1)

    assert "part=1" in repr(f1)
    assert "part=" not in repr(f0)
