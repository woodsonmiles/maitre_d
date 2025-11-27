# cli.py
import typer
from pathlib import Path
from family import Family
from payment import Payment
from typing import List, Set
from pay_check import families_with_payments

app = typer.Typer()

@app.command()
def mail_invitations():
    """Create list of letter to mail with address, number of tickets and name"""
    package_root = Path(__file__).parent
    guest_list_path = package_root / 'data' / 'guest-list.csv'
    payment_path = package_root / 'data' / 'payment.csv'
    families: Set = Family.from_csv(guest_list_path)
    payments: List = Payment.from_csv(payment_path)
    paid_families: Set = families_with_payments(families, payments)
    unpaid_families: 

if __name__ == "__main__":
    app()

