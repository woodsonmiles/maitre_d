# cli.py
import typer
from pathlib import Path
from family import Family
from payment import Payment
from invitation import Invitation
from typing import Dict, Set, List
from matcher import match_families_with_payments
from seating_chart import create_area_aware_seating
from seating_requests import extract_families_from_request, print_requests_map
from write_seating_results import write_seating_results

app = typer.Typer()

def match_families():
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
    # write out unmatched payments
    payments_file = Path.cwd() / 'unmatched_payments.csv'
    Payment.to_csv(list(unmatched_payments), payments_file)
    # write out unmatched families
    families_file = Path.cwd() / 'unmatched_families.csv'
    Family.to_csv(list(unmatched_families), families_file)
    return matched_families


@app.command()
def mail_invitations():
    """
    Write three CSVs to working directory
    invitations.csv
    unmatched_payments.csv
    unmatched_families.csv
    """
    # write out invitations
    matched_families = match_families()
    invitations: List[Invitation] = Invitation.from_families(list(matched_families))
    invitation_file = Path.cwd() / 'invitations.csv'
    Invitation.to_csv(invitations, invitation_file)

@app.command()
def assign_tables():
    """
    Write a CSV of guests assigned to tables
    Earliest reservations take priority in seating requests
    """
    matched_families = match_families()
    # sort by submission time
    sorted_families: List = sorted(matched_families, key=lambda family: family.submission)
    last_to_first: Dict = Family.last_to_firstnames(sorted_families)
    last_to_family: Dict = Family.last_to_family(sorted_families)

    request_map = {}
    for family in sorted_families:
        requests = extract_families_from_request(request_string=family.requests, last_to_firstnames=last_to_first, last_to_families=last_to_family)
        request_map[family] = requests

    print_requests_map(request_map)

    areas, conflicts, layout = create_area_aware_seating(families_sorted=sorted_families, requests_map=request_map, table_size=10, debug=False)
    areas_path = Path.cwd() / 'areas.yaml'
    conflicts_path = Path.cwd() / 'conflicts.yaml'
    write_seating_results(areas, conflicts, layout, areas_path, conflicts_path)


if __name__ == "__main__":
    app()

