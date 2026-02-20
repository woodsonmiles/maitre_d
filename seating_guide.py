import yaml
from pathlib import Path

def build_seating_guide(yaml_path: Path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    entries = []

    # data structure: { area: { table: [families...] } }
    for tables in data.values():
        for table, families in tables.items():
            for fam in families:
                last = fam["last"].strip().title()
                first_initial = fam["first"].strip().title()[0]
                entries.append((last, first_initial, table))

    # Sort by last name, then first initial
    entries.sort(key=lambda x: (x[0].lower(), x[1].lower()))

    return entries

def write_seating_guide(entries, output_path: Path):
    """
    Write a list of (last, first_initial, table_number) tuples
    to a file, one entry per line.

    Format: "Last, F. — Table X"
    """
    lines = [
        f"{last}, {initial}. — Table {table}"
        for last, initial, table in entries
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")

