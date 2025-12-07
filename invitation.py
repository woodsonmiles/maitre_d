from dataclasses import dataclass, asdict
from family import Family
from typing import List
import csv
from pathlib import Path
import usaddress

@dataclass
class Invitation:
    last_name: str
    first_name: str
    num_tickets: int
    address1: str
    address2: str


    @classmethod
    def from_families(cls, families: List[Family]):
        invitations = []
        for family in families:
            adult = family.guests[0]
            parsed_address: dict[str, str] = {}
            address_type: str = ""
            try:
                parsed_address, address_type = usaddress.tag(family.address)
            except usaddress.RepeatedLabelError :
                print(f'Bad address: {family.address}')
            if address_type == 'PO Box':
                box = parsed_address.get('USPSBoxID','')
                address1 = f'P.O. Box {box}'.strip()
            else:
                addr_num = parsed_address.get('AddressNumber','')
                street_name=parsed_address.get('StreetName','').title().strip()
                street_type=parsed_address.get('StreetNamePostType','').title()
                address1 = f'{addr_num} {street_name} {street_type}'.strip()
            
            city=parsed_address.get('PlaceName','').title()
            state=parsed_address.get('StateName','')
            zip_code=parsed_address.get('ZipCode','')
            address2 = f'{city}, {state} {zip_code}'.strip()
            invitations.append(
                Invitation(
                    first_name=adult.first_name,
                    last_name=adult.last_name,
                    num_tickets=len(family.guests),
                    address1=address1,
                    address2=address2
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
