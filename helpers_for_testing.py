from family import Family, Guest, Meal
from datetime import datetime
# ---------------------------------------------------------
# Helper: minimal Family factory for testing
# ---------------------------------------------------------

def make_family(first: str, last: str, size: int = 1, requests: str = '') -> Family:
    """
    Create a Family object suitable for seating_chart tests.

    seating_chart.py only depends on:
      - first_name / last_name (derived from guests)
      - size (len(guests))
      - to_dict()

    All other fields can be safely filled with defaults.
    """
    guest = make_guest(first, last)
    guests = []
    # Add placeholder guests to match requested size
    for _ in range(size):
        guests.append(guest)

    return Family(
        email=f"{first}.{last}@example.com",
        phone=f"{first}.{last}",
        address=f"{first}.{last}",
        requests=requests,            # raw request string not used by seating_chart
        submission=datetime.now(),
        guests=guests,
    )

def make_guest(first: str, last: str) -> Guest:
    return Guest(
            first_name=first,
            last_name=last,
            age=30,
            allergies='',
            meal_choice=Meal.Chicken
    )
