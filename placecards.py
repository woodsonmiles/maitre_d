from typing import Dict, List
from collections import defaultdict
from family import Family, Guest, Meal
from pathlib import Path
import yaml
import csv
from pathlib import Path

def extract_tables_from_areas(yaml_path: Path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data.values()


def expand_areas_to_guests(
    areas: Dict[str, Dict[str, List[dict]]],
    email_lookup: Dict[str, "Family"],
) -> Dict[str, List["Guest"]]:
    """
    Convert a mapping of area -> table -> list of family dicts
    into a mapping of table -> list of Guest objects.

    If a family email is missing from email_lookup, create placeholder Guests
    based on the 'size' attribute.
    """
    result: Dict[str, List["Guest"]] = defaultdict(list)

    for tables in areas.values():
        for raw_table_name, family_dicts in tables.items():
            table_name = str(raw_table_name)
            for fam_dict in family_dicts:
                email = fam_dict["email"]
                size = fam_dict["size"]

                if email in email_lookup:
                    family = email_lookup[email]
                    result[table_name].extend(family.guests)
                else:
                    # Create placeholder guests
                    placeholder_guests = [
                        Guest(
                            first_name=f"Guest{i+1}",
                            last_name=f"{email}",
                            meal_choice=Meal.Chicken,  # or your default
                            allergies="",
                            age=0,
                        )
                        for i in range(size)
                    ]
                    result[table_name].extend(placeholder_guests)

    return dict(result)


def write_guest_csv(table_to_guests: Dict[str, List["Guest"]], output_path: Path):
    """
    Write a CSV file with one row per guest.
    Columns: table, first_name, last_name, meal_choice, allergies, age
    Tables are sorted alphabetically.
    """
    fieldnames = [
        "table",
        "first_name",
        "last_name",
        "meal_choice",
        "allergies",
        "age",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for table_name in sorted(table_to_guests.keys(), key=table_sort_key):
            for guest in table_to_guests[table_name]:
                writer.writerow({
                    "table": table_name,
                    "first_name": guest.first_name,
                    "last_name": guest.last_name,
                    "meal_choice": guest.meal_choice.name,  # or .value
                    "allergies": guest.allergies,
                    "age": guest.age,
                })

def table_sort_key(name: str):
    """
    Numeric table names sort numerically ascending.
    String table names sort by length, then alphabetically.
    """
    if name.isdigit():
        return (0, int(name))
    return (1, len(name), name.lower())
