# cli.py
import typer
from pathlib import Path
from family import Family
from payment import Payment
from invitation import Invitation
from typing import Set, List
from matcher import match_families_with_payments

app = typer.Typer()

@app.command()
def mail_invitations():
    """
    Write three CSVs to working directory
    invitations.csv
    unmatched_payments.csv
    unmatched_families.csv
    """
    package_root = Path(__file__).parent
    guest_list_path = package_root / 'data' / 'guest-list.csv'
    payment_path = package_root / 'data' / 'payment.csv'
    families: Set = Family.from_csv(guest_list_path)
    # for family in families:
    #     print(family)
    unique_families: Set = Family.unique(families)
    payments: Set = Payment.from_csv(payment_path)
    matched_families, matched_payments = match_families_with_payments(families=unique_families, payments=payments)
    print("Matched:")
    print(f"  Payments: {len(matched_payments)}")
    print(f"  Families: {len(matched_families)}")
    unmatched_payments = payments - matched_payments
    unmatched_families = families - matched_families
    print("Unmatched:")
    print(f"  Payments: {len(unmatched_payments)}")
    print(f"  Families: {len(unmatched_families)}")
    # write out invitations
    invitations: List[Invitation] = Invitation.from_families(list(matched_families))
    invitation_file = Path.cwd() / 'invitations.csv'
    Invitation.to_csv(invitations, invitation_file)
    # write out unmatched payments
    payments_file = Path.cwd() / 'unmatched_payments.csv'
    Payment.to_csv(list(unmatched_payments), payments_file)
    # write out unmatched families
    families_file = Path.cwd() / 'unmatched_families.csv'
    Family.to_csv(list(unmatched_families), families_file)

@app.command()
def assign_tables():
    """
    Write a CSV of guests assigned to tables
    Earliest reservations take priority in seating requests
    """
    package_root = Path(__file__).parent
    guest_list_path = package_root / 'data' / 'guest-list.csv'
    families: Set = Family.from_csv(guest_list_path)
    unique_families: Set = Family.unique(families)
    # sort by submission time
    sorted_families: List = sorted(unique_families, key=lambda family: family.submission)

    # for each family, for each request,
    # add requested families until either there are no more requests or the table is full
    # requested families

    # build list of tables satisfying requests
    # A table is simply a list of up to 10 guests


if __name__ == "__main__":
    app()

