from dataclasses import dataclass

@dataclass
class Invitation:
    first_name: str
    last_name: str
    num_tickets: int
    address: str

