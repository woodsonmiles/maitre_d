import csv, phonenumbers
from dataclasses import dataclass, field
from typing import List, Set
from enum import Enum
from phone import normalize_phone

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
                        guests=guests
                    ))
        return families

    def __hash__(self):
        return hash(self.email)

    def __eq__(self, other):
        if not isinstance(other, Family):
            return False
        return self.email == other.email

def coerce_meal(value: str) -> Meal:
    try:
        return Meal[value]  # lookup by name
    except KeyError:
        return Meal.Chicken

