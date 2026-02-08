import yaml
from pathlib import Path

def write_seating_results(areas, conflicts, layout, areas_path: Path, conflicts_path: Path):
    print("\n==================== SEATING LAYOUT ====================")
    print(layout)
    print("========================================================\n")

    # ----------------------------------------------------
    # 1. Build nested structure: areas → global tables
    # ----------------------------------------------------
    areas_serializable = {}
    global_table_id = 0

    for area_idx in sorted(areas.keys()):
        tables = areas[area_idx]

        # Each area becomes a dict of table_id → families
        area_map = {}

        for table in tables:
            area_map[global_table_id] = [fam.to_dict() for fam in table]
            global_table_id += 1

        areas_serializable[area_idx] = area_map

    # ----------------------------------------------------
    # 2. Convert conflicts to serializable form
    # ----------------------------------------------------
    conflicts_serializable = [
        {
            "family": fam.to_dict(),
            "requested": requested.to_dict(),
            "reason": reason,
        }
        for fam, requested, reason in conflicts
    ]

    # ----------------------------------------------------
    # 3. Write YAML files
    # ----------------------------------------------------
    with open(areas_path, "w") as f:
        yaml.dump(areas_serializable, f, sort_keys=True)

    with open(conflicts_path, "w") as f:
        yaml.dump(conflicts_serializable, f, sort_keys=False)
