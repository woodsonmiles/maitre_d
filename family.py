import csv, phonenumbers
from dataclasses import dataclass, field
from typing import List, Set
from enum import Enum
from phone import normalize_phone
from pathlib import Path

Meal = Enum("Meal", ["Vegan", "Chicken", "Allergy", "Beef", "Kid-Friendly"])

@dataclass
class Guest:
    first_name: str
    last_name: str
    meal_choice: Meal
    allergies: str
    age: int

@dataclass
class Family:
    email: str
    phone: str
    address: str
    requests: str
    guests: List[Guest] = field(default_factory=list)

    @classmethod
    def from_csv(cls, filepath) ->Set["Family"]:
        """Deserialize a CSV file into a list of Families"""
        families = set()
        with open(filepath, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                guests = []
                num_tickets=int(row["Tickets"])
                for ticket in range(1, num_tickets+1):
                    first_name = row.get(f"First Name (Ticket {ticket})")
                    if first_name:
                        guests.append(Guest(
                            first_name=first_name,
                            last_name=row.get(f"Last Name (Ticket {ticket})", ''),
                            age=int(row.get(f"Age (Ticket {ticket})") or 0),
                            meal_choice=coerce_meal(row.get(f"Meal Choice (Ticket {ticket})", "Chicken")),
                            allergies=row.get(f"List Allergies (Ticket {ticket})", '')
                        ))
                if num_tickets > 0:
                    families.add(cls(
                        email=row.get("Email", ''),
                        phone=normalize_phone(row.get("Phone",'')),
                        guests=guests,
                        address=row["Mailing Address"],
                        requests=row.get("Additional Requests:", "")
                    ))
        return families

    @classmethod
    def unique(cls, families: Set["Family"]) -> Set["Family"]:
        seen_phones = set()
        seen_addresses = set()
        unique_families = set()
        for family in families:
            if family.phone in seen_phones or family.address in seen_addresses:
                continue  # skip duplicate
            unique_families.add(family)
            seen_phones.add(family.phone)
            seen_addresses.add(family.address)
        return unique_families

    def oldest_guest(self):
        return max(self.guests, key=lambda g: g.age)

    def __hash__(self):
        return hash(self.email)

    def __eq__(self, other):
        if not isinstance(other, Family):
            return False
        return self.email == other.email

    @classmethod
    def to_csv(cls, families: List["Family"], filepath: Path) -> None:
        """Serialize a list of Family objects into a CSV file."""
        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=["Email", "Phone", "First Name", "Last Name", "Address", "Tickets"]
            )
            writer.writeheader()
            for fam in families:
                adult=fam.oldest_guest()
                writer.writerow({
                    "Email": fam.email,
                    "Phone": fam.phone,
                    "First Name": adult.first_name,
                    "Last Name": adult.last_name,
                    "Address": fam.address,
                    "Tickets": len(fam.guests)
                })

def coerce_meal(value: str) -> Meal:
    try:
        return Meal[value]  # lookup by name
    except KeyError:
        return Meal.Chicken

