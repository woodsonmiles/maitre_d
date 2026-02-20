import yaml
from pathlib import Path
from collections import defaultdict

def get_table_sizes(yaml_path: Path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    sizes = defaultdict(list)
    for tables in data.values():
        for table, families in tables.items():
            size = sum(fam_yaml['size'] for fam_yaml in families)
            sizes[size].append(table)
    return sizes


def write_table_sizes(sizes: dict, output_path: Path, num_guests: int, num_families: int):
    """
    Write a map of table sizes to tables
    """
    with open(output_path, 'w') as f:
        f.write(f"Guests: {num_guests}\n")
        f.write(f"Families: {num_families}\n")
        for size in sorted(sizes.keys()):
            f.write(f"{size}:\n")
            for table in sizes[size]:
                f.write(f"  {table}\n")


def get_num_guests(yaml_path: Path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    num_guests = 0
    for tables in data.values():
        for families in tables.values():
            table_size = sum(fam_yaml['size'] for fam_yaml in families)
            num_guests += table_size
    return num_guests
        

def get_num_families(yaml_path: Path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    num_families = 0
    for tables in data.values():
        num_families += len(tables.values())
    return num_families

