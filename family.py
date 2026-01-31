import csv
from dataclasses import dataclass, field
from typing import Dict, List, Set
from enum import Enum
from datetime import datetime
from collections import defaultdict

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
    submission: datetime
    guests: List[Guest] = field(default_factory=list)

    @property
    def first_name(self):
        return self.guests[0].first_name

    @property
    def last_name(self):
        return self.guests[0].last_name

    @property
    def size(self):
        return len(self.guests)

    def oldest_guest(self):
        return self.guests[0]

    def __repr__(self) -> str:
        return f"Family({self.email})"

    def __hash__(self):
        return hash(self.email)

    def __eq__(self, other):
        if not isinstance(other, Family):
            return False
        return self.email == other.email

    def to_dict(self) -> Dict:
        return {
            "email": self.email,
            "size": self.size
        }

    @classmethod
    def from_csv(cls, filepath) ->Set["Family"]:
        """Deserialize a CSV file into a list of Families"""
        families = set()
        with open(filepath, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                guests = []
                num_tickets=int(row["Tickets"])                
                for ticket in range(1, num_tickets+1):
                    first_name = row[f"First Name (Ticket {ticket})"]
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
                        email=row.get("Email", '').lower(),
                        phone=normalize_phone(row.get("Phone",'')),
                        guests=guests,
                        address=row["Mailing Address"],
                        requests=row.get("Additional Requests:", ""),
                        submission=datetime.fromisoformat(row["Submission time"])

                    ))
        return families

    @staticmethod
    def unique(families: Set["Family"]) -> Set["Family"]:
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



    @staticmethod
    def to_csv(families: List["Family"], filepath: Path) -> None:
        """Serialize a list of Family objects into a CSV file."""
        sorted_families = sorted(families, key=lambda f: f.oldest_guest().last_name)
        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=["Last Name", "First Name", "Email", "Phone", "Tickets", "Address"]
            )
            writer.writeheader()
            for fam in sorted_families:
                adult=fam.oldest_guest()
                writer.writerow({
                    "Email": fam.email,
                    "Phone": fam.phone,
                    "First Name": adult.first_name,
                    "Last Name": adult.last_name,
                    "Address": fam.address,
                    "Tickets": len(fam.guests)
                })

    @staticmethod
    def last_to_firstnames(families: List["Family"]) -> Dict:
        """Return map of family last name (Dad's) to Dad's first name"""
        last_to_first = defaultdict(list)
        for family in families:
            last_to_first[family.last_name].append(family.first_name)
        return last_to_first

    @staticmethod
    def last_to_family(families: List["Family"]) -> Dict:
        """Return map of family last name (Dad's) to Dad's first name"""
        last_to_family = defaultdict(list)
        for family in families:
            last_to_family[family.last_name].append(family)
        return last_to_family

def coerce_meal(value: str) -> Meal:
    try:
        return Meal[value]  # lookup by name
    except KeyError:
        return Meal.Chicken

