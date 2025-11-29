import csv
from dataclasses import asdict, dataclass
from typing import Set, List
from phone import normalize_phone
from pathlib import Path


@dataclass
class Payment:
    last_name: str
    first_name: str
    email: str
    phone: str
    order_number: str

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

    @staticmethod
    def to_csv(payments: List["Payment"], filename: Path) -> None:
        """
        Write a list of Payment instances to a CSV file.
        Always overwrites the file with the new data.
        
        Args:
            payments (List[Payment]): List of Payment objects to write.
            filename (str): Path to the CSV file.
        """
        if not payments:
            return  # Nothing to write

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=asdict(payments[0]).keys())
            writer.writeheader()
            for payment in payments:
                writer.writerow(asdict(payment))
