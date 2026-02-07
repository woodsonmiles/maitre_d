import pytest
from io import StringIO
from pathlib import Path
from datetime import datetime
import yaml

from family import Family, Guest, Meal
from seating_requests import extract_families_from_request
from seating_chart import create_area_aware_seating
from write_seating_results import write_seating_results
from helpers_for_testing import make_family

# ---------------------------------------------------------
# End-to-end test
# ---------------------------------------------------------

def test_end_to_end_pipeline(tmp_path):
    """
    Full integration test that mirrors the CLI's assign_tables() flow,
    using real temporary files instead of monkeypatched open().
    """

    # Build families (as before)
    smith1 = make_family("John", "Smith", 4, requests="Please seat us with Ava Jones")
    smith2 = make_family("Paul", "Smith", 3)
    jones  = make_family("Ava", "Jones", 2)

    families = {smith1, smith2, jones}

    # Deduplicate
    unique_families = Family.unique(families)

    # Sort
    sorted_families = sorted(unique_families, key=lambda f: f.submission)

    # Build lookup maps
    last_to_first = Family.last_to_firstnames(sorted_families)
    last_to_family = Family.last_to_family(sorted_families)

    # Build request map
    request_map = {}
    for fam in sorted_families:
        reqs = extract_families_from_request(
            request_string=fam.requests,
            last_to_firstnames=last_to_first,
            last_to_families=last_to_family,
        )
        request_map[fam] = reqs

    # Run seating engine
    areas, conflicts, layout = create_area_aware_seating(
        families_sorted=sorted_families,
        requests_map=request_map,
        table_size=10,
        debug=False,
    )

    # Write results to real temp files
    areas_path = tmp_path / "areas.yaml"
    conflicts_path = tmp_path / "conflicts.yaml"

    write_seating_results(areas, conflicts, layout, areas_path, conflicts_path)

    # Read them back
    areas_yaml = areas_path.read_text()
    conflicts_yaml = conflicts_path.read_text()

    # Assertions
    assert "Smith" in areas_yaml
    assert "Jones" in areas_yaml
    conflicts_data = yaml.safe_load(conflicts_yaml)
    assert conflicts_data == [] # no conflicts

