import yaml
from pathlib import Path

def write_seating_results(areas, conflicts, layout, areas_path: Path, conflicts_path: Path):
    """
    Writes seating results to YAML files and prints the human-readable layout.

    Parameters:
        areas (dict[int, list[list[Family]]]):
            Mapping of area index → list of tables → list of Family objects.

        conflicts (list[(Family, Family, str)]):
            List of unmet seating requests.

        layout (str):
            Human-readable seating layout (printed to screen).

        areas_path (str):
            Output path for serialized areas YAML.

        conflicts_path (str):
            Output path for serialized conflicts YAML.
    """

    # ----------------------------------------------------
    # 1. Print layout to screen
    # ----------------------------------------------------
    print("\n==================== SEATING LAYOUT ====================")
    print(layout)
    print("========================================================\n")

    # ----------------------------------------------------
    # 2. Convert areas to serializable form
    # ----------------------------------------------------
    areas_serializable = {
        area_idx: [
            [fam.to_dict() for fam in table]
            for table in tables
        ]
        for area_idx, tables in areas.items()
    }

    # ----------------------------------------------------
    # 3. Convert conflicts to serializable form
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
    # 4. Write YAML files
    # ----------------------------------------------------
    with open(areas_path, "w") as f:
        yaml.dump(areas_serializable, f, sort_keys=True)

    with open(conflicts_path, "w") as f:
        yaml.dump(conflicts_serializable, f, sort_keys=False)
