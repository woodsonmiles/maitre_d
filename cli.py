# cli.py
import typer
from pathlib import Path
from family import Family
from payment import Payment
from typing import List, Set
from matcher import match_families_with_payments

app = typer.Typer()

@app.command()
def mail_invitations():
    """Create list of letter to mail with address, number of tickets and name"""
    package_root = Path(__file__).parent
    guest_list_path = package_root / 'data' / 'guest-list.csv'
    payment_path = package_root / 'data' / 'payment.csv'
    families: Set = Family.from_csv(guest_list_path)
    payments: Set = Payment.from_csv(payment_path)
    matched_families, matched_payments = match_families_with_payments(families, payments)
    print("Matched:")
    print(f"  Payments: {len(matched_payments)}")
    print(f"  Families: {len(matched_families)}")
    unmatched_payments = payments - matched_payments
    unmatched_families = families - matched_families
    print("Unmatched:")
    print(f"  Payments: {len(unmatched_payments)}")
    print(f"  Families: {len(unmatched_families)}")

    print("Payments:")
    for payment in unmatched_payments:
        print(payment)
    print("Families:")
    for family in unmatched_families:
        print(family)

if __name__ == "__main__":
    app()

