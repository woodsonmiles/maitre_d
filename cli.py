# cli.py
import typer
from pathlib import Path
from family import Family
from payment import Payment
from invitation import Invitation
from typing import Set
from matcher import match_families_with_payments

app = typer.Typer()

@app.command()
def mail_invitations():
    """Create list of letter to mail with address, number of tickets and name"""
    package_root = Path(__file__).parent
    guest_list_path = package_root / 'data' / 'guest-list.csv'
    payment_path = package_root / 'data' / 'payment.csv'
    families: Set = Family.from_csv(guest_list_path)
    unique_families: Set = Family.unique(families)
    payments: Set = Payment.from_csv(payment_path)
    matched_families, matched_payments = match_families_with_payments(unique_families, payments)
    print("Matched:")
    print(f"  Payments: {len(matched_payments)}")
    print(f"  Families: {len(matched_families)}")
    unmatched_payments = payments - matched_payments
    unmatched_families = families - matched_families
    print("Unmatched:")
    print(f"  Payments: {len(unmatched_payments)}")
    print(f"  Families: {len(unmatched_families)}")

    invitations = []
    for family in matched_families:
        adult = family.oldest_guest()
        invitations.append(
            Invitation(
                first_name=adult.first_name,
                last_name=adult.last_name,
                num_tickets=len(family.guests),
                address=family.address
            )
        )


if __name__ == "__main__":
    app()

