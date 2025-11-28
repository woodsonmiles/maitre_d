from dataclasses import dataclass
from family import Family
from typing import List
import csv
from pathlib import Path

@dataclass
class Invitation:
    first_name: str
    last_name: str
    num_tickets: int
    address: str

    @classmethod
    def from_families(cls, families: List[Family]):
        invitations = []
        for family in families:
            adult = family.oldest_guest()
            invitations.append(
                Invitation(
                    first_name=adult.first_name,
                    last_name=adult.last_name,
                    num_tickets=len(family.guests),
                    address=family.address
                )
            )
        return invitations

    @classmethod
    def to_csv(cls, invitations: List["Invitation"], filepath: Path) -> None:
        """Serialize a list of Invitations into a CSV file."""
        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=["First Name", "Last Name", "Tickets", "Address"]
            )
            writer.writeheader()
            for inv in invitations:
                writer.writerow({
                    "First Name": inv.first_name,
                    "Last Name": inv.last_name,
                    "Tickets": inv.num_tickets,
                    "Address": inv.address
                })
