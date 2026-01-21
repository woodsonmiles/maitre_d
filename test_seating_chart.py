import pytest

# Import your seating engine functions here
from seating_chart import (
    build_clusters,
    assign_clusters_to_areas,
    place_cluster_into_area,
    generate_conflict_report,
    visualize_areas,
    create_area_aware_seating
)

# Minimal Family class for testing
class Family:
    def __init__(self, last_name, size, requests=None):
        self.last_name = last_name
        self.size = size
        self.requests = requests or []

    def __repr__(self):
        return f"Family({self.last_name}, {self.size})"


# ---------------------------------------------------------
# CLUSTER TESTS
# ---------------------------------------------------------

def test_cluster_simple():
    """Two families requesting each other should form a single cluster."""
    a = Family("Smith", 4, ["Jones"])
    b = Family("Jones", 3, ["Smith"])
    families = [a, b]
    requests = {a: a.requests, b: b.requests}

    clusters = build_clusters(families, requests)

    assert len(clusters) == 1
    assert set(clusters[0]) == {a, b}


def test_cluster_disconnected():
    """Families with no requests should form separate clusters."""
    a = Family("Smith", 4)
    b = Family("Jones", 3)
    families = [a, b]
    requests = {a: [], b: []}

    clusters = build_clusters(families, requests)

    assert len(clusters) == 2


# ---------------------------------------------------------
# AREA ASSIGNMENT TESTS
# ---------------------------------------------------------

def test_area_assignment_creates_new_area():
    """A cluster too large for existing areas should create a new area."""
    a = Family("Smith", 6)
    b = Family("Jones", 6)
    clusters = [[a, b]]

    gen = assign_clusters_to_areas(clusters, tables_per_area=1, table_size=10, debug=False)
    action, area_index, assigned_cluster = next(gen)

    assert action == "new"
    assert area_index == 0


def test_area_assignment_reuses_area():
    """A second cluster should reuse an area if capacity allows."""
    a = Family("Smith", 4)
    b = Family("Jones", 4)
    c = Family("Brown", 4)

    clusters = [[a, b], [c]]

    gen = assign_clusters_to_areas(clusters, tables_per_area=2, table_size=10, debug=False)
    first = next(gen)
    second = next(gen)

    assert second[0] == "existing"
    assert second[1] == 0


# ---------------------------------------------------------
# TABLE PLACEMENT TESTS
# ---------------------------------------------------------

def test_table_placement_respects_requests():
    """Families should be placed near requested families when possible."""
    a = Family("Smith", 4, ["Jones"])
    b = Family("Jones", 4)

    area_tables = []
    place_cluster_into_area([b, a], area_tables, table_size=10, tables_per_area=3, debug=False)

    # Smith should be placed at the same table as Jones
    assert area_tables[0] == [b, a]


def test_table_overflow_moves_to_next_table():
    """Families should overflow to the next table when one is full."""
    a = Family("A", 10)
    b = Family("B", 10)

    area_tables = []
    place_cluster_into_area([a, b], area_tables, table_size=10, tables_per_area=3, debug=False)

    assert area_tables[0] == [a]
    assert area_tables[1] == [b]


# ---------------------------------------------------------
# CONFLICT REPORT TESTS
# ---------------------------------------------------------

def test_conflict_report_detects_unmet_requests():
    """Families not seated in the same area as requested families should appear in conflict report."""
    a = Family("Smith", 4, ["Jones"])
    b = Family("Jones", 4)

    areas = {
        0: [[a]],   # Area 0
        1: [[b]]    # Area 1
    }

    requests = {a: a.requests, b: b.requests}
    conflicts = generate_conflict_report(areas, requests)

    assert len(conflicts) == 1
    fam, last, reason = conflicts[0]
    assert fam == a
    assert last == "Jones"


# ---------------------------------------------------------
# VISUALIZATION TESTS
# ---------------------------------------------------------

def test_visualization_format():
    """Visualization should contain area and table headers."""
    a = Family("Smith", 4)
    areas = {0: [[a]]}

    layout = visualize_areas(areas)

    assert "AREA 0" in layout
    assert "Table 0" in layout
    assert "Smith" in layout


# ---------------------------------------------------------
# FULL PIPELINE TEST
# ---------------------------------------------------------

def test_full_pipeline():
    """End-to-end test of the full seating engine."""
    a = Family("Smith", 4, ["Jones"])
    b = Family("Jones", 4)
    c = Family("Brown", 4)

    families_sorted = [a, b, c]
    requests = {a: a.requests, b: b.requests, c: c.requests}

    areas, conflicts, layout = create_area_aware_seating(
        families_sorted,
        requests,
        table_size=10,
        tables_per_area=2,
        debug=False
    )

    # Smith and Jones should be in the same area
    smith_area = next(idx for idx, tables in areas.items() if a in sum(tables, []))
    jones_area = next(idx for idx, tables in areas.items() if b in sum(tables, []))

    assert smith_area == jones_area

    # Layout should not be empty
    assert len(layout) > 0

