from datetime import datetime
import pytest
from family import Family
from payment import Payment
from pathlib import Path
from matcher import (
    families_with_payment_email,
    families_with_payment_phone,
    families_with_payment,
    get_matched_payments,
    match_families_with_payments,
)

package_root = Path(__file__).parent
guest_list_path = package_root / 'data' / 'guest-list.csv'
payment_path = package_root / 'data' / 'payment.csv'

def make_family(email: str, phone: str):
    return Family(
        email=email,
        phone=phone,
        address='',
        requests='',
        submission=datetime.now()
    )

def test_family_equal():
    alice1 = make_family(email="alice@example.com", phone="1111"),  # match both
    alice2 = make_family(email="alice@example.com", phone="2222"),  # match both
    david = make_family(email="david@example.com", phone="1111"),  # match phone
    assert alice1 == alice2
    assert alice1 != david

def test_family_from_csv():
    families = Family.from_csv(guest_list_path)
    assert len(families) >= 20

def test_payment_from_csv():
    payments = Payment.from_csv(payment_path)
    assert len(payments) >= 120

@pytest.fixture
def sample_data():
    payments = {
        Payment(order_number="1", first_name="Alice", last_name="Smith", email="alice@example.com", phone="1111"),
        Payment(order_number="2", first_name="Bob", last_name="Jones", email="bob@example.com", phone="2222"),
        Payment(order_number="3", first_name="Charlie", last_name="Brown", email="charlie@example.com", phone="3333"),  # no match
        Payment(order_number="4", first_name="Dug", last_name="Von", email="dug@example.com", phone="5555"),
    }
    families = {
        make_family(email="alice@example.com", phone="1111"),  # match both
        make_family(email="david@example.com", phone="2222"),  # match phone
        make_family(email="eve@example.com", phone="4444"),    # no match
        make_family(email="dug@example.com", phone="6666"),    # match email
    }
    return payments, families


def test_families_with_payment_email(sample_data):
    payments, families = sample_data
    matched = families_with_payment_email(families=families, payments=payments)
    emails = {f.email for f in matched}
    assert "alice@example.com" in emails
    assert "david@example.com" not in emails


def test_families_with_payment_phone(sample_data):
    payments, families = sample_data
    matched = families_with_payment_phone(families=families, payments=payments)
    print("matched")
    print(matched)
    emails = {f.email for f in matched}
    assert "alice@example.com" in emails
    assert "david@example.com" in emails
    assert "eve@example.com" not in emails
    assert "charlie@example.com" not in emails
    assert "dug@example.com" not in emails
    phones = {f.phone for f in matched}
    assert "1111" in phones
    assert "2222" in phones
    assert "4444" not in phones


def test_families_with_payment_union(sample_data):
    payments, families = sample_data
    matched = families_with_payment(families=families, payments=payments)
    emails = {f.email for f in matched}
    assert "alice@example.com" in emails
    assert "david@example.com" in emails
    assert "eve@example.com" not in emails
    assert "charlie@example.com" not in emails


def test_get_matched_payments(sample_data):
    payments, families = sample_data
    matched_families = families_with_payment(families=families, payments=payments)
    matched = get_matched_payments(payments=payments, matched_families=matched_families)
    emails = {p.email for p in matched}
    assert "alice@example.com" in emails
    assert "bob@example.com" in emails
    assert "charlie@example.com" not in emails
    assert "eve@example.com" not in emails


def test_match_families_with_payment(sample_data):
    payments, families = sample_data
    matched_families, get_matched_payments_set = match_families_with_payments(families=families, payments=payments)
    assert any(f.email == "alice@example.com" for f in matched_families)
    assert any(p.email == "alice@example.com" for p in get_matched_payments_set)
    # Ensure unmatched families are excluded
    assert all(f.email != "eve@example.com" for f in matched_families)
    assert all(f.email != "charlie@example.com" for f in matched_families)

