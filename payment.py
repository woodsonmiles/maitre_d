import csv
from dataclasses import dataclass
from typing import Set
from phone import normalize_phone


@dataclass
class Payment:
    order_number: str
    first_name: str
    last_name: str
    email: str
    phone: str

    @classmethod
    def from_csv(cls, filepath) -> Set["Payment"]:
        """Deserialize a CSV file into a list of Payment objects."""
        payments = set()
        with open(filepath, newline="", encoding="utf-16") as csvfile:
            reader = csv.DictReader(csvfile, delimiter="\t")
            for row in reader:
                payments.add(cls(
                    order_number=row["Order number"],
                    first_name=row["Guest first name"],
                    last_name=row["Guest last name"],
                    email=row["Email"],
                    phone=normalize_phone(row.get("Phone Number",'')),
                ))
        return payments

    def __hash__(self):
        return hash(self.order_number)

    def __eq__(self, other):
        if not isinstance(other, Payment):
            return False
        return self.order_number == other.order_number

