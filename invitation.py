from dataclasses import dataclass, asdict
from family import Family
from typing import List
import csv
from pathlib import Path

import payment

@dataclass
class Invitation:
    last_name: str
    first_name: str
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

    @staticmethod
    def to_csv(invitations: List["Invitation"], filepath: Path) -> None:
        """Write a list of Invitations to a CSV file, sorted by last name."""
        sorted_invitations = sorted(invitations, key=lambda i: i.last_name)
        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=asdict(sorted_invitations[0]).keys()
            )
            writer.writeheader()
            for inv in sorted_invitations:
                writer.writerow(asdict(inv))
