from family import Family
from payment import Payment
from typing import Set, Tuple

def match_families_with_payments(families: Set[Family], payments: Set[Payment]) -> Tuple[Set[Family], Set[Payment]]:
    matched_families = families_with_payment(families, payments)
    matched_payments = get_matched_payments(matched_families, payments)
    return matched_families, matched_payments


def families_with_payment(families: Set[Family], payments: Set[Payment]) -> Set[Family]:
    # Union of both sets
    email = families_with_payment_email(families, payments) 
    phone = families_with_payment_phone(families, payments)
    return email | phone

def families_with_payment_email(families: Set[Family], payments: Set[Payment]) -> Set[Family]:
    payment_emails = {p.email for p in payments if p.email}
    return {f for f in families if f.email in payment_emails}

def families_with_payment_phone(families: Set[Family], payments: Set[Payment]) -> Set[Family]:
    payment_phones = {p.phone for p in payments if p.phone}
    return {f for f in families if f.phone in payment_phones}

def get_matched_payments(matched_families: Set[Family], payments: Set[Payment]) -> Set[Payment]:
    matched_emails = {f.email for f in matched_families if f.email}
    matched_phones = {f.phone for f in matched_families if f.phone}
    return {
        p for p in payments
        if (p.email in matched_emails or p.phone in matched_phones)
    }
