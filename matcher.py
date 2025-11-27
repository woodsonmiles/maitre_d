from family import Family
from payment import Payment
from typing import Set, Tuple

def match_families_with_payments(payments: Set[Payment], families: Set[Family]) -> Tuple[Set[Family], Set[Payment]]:
    matched_families = families_with_payment_email(payments, families) | families_with_payment_phone(payments, families)
    matched_payments = get_matched_payments(payments, matched_families)
    return matched_families, matched_payments


def families_with_payments(payments: Set[Payment], families: Set[Family]) -> Set[Family]:
    # Union of both sets
    return families_with_payment_email(payments, families) | families_with_payment_phone(payments, families)

def families_with_payment_email(payments: Set[Payment], families: Set[Family]) -> Set[Family]:
    payment_emails = {p.email for p in payments if p.email}
    return {f for f in families if f.email in payment_emails}

def families_with_payment_phone(payments: Set[Payment], families: Set[Family]) -> Set[Family]:
    payment_phones = {p.phone for p in payments if p.phone}
    return {f for f in families if f.phone in payment_phones}

def get_matched_payments(payments: Set[Payment], matched_families: Set[Family]) -> Set[Payment]:
    matched_emails = {f.email for f in matched_families if f.email}
    matched_phones = {f.phone for f in matched_families if f.phone}
    return {
        p for p in payments
        if (p.email in matched_emails or p.phone in matched_phones)
    }
