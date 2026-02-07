import pytest
from typing import Dict, List

from seating_chart import (
    build_clusters,
    assign_cluster_to_area,
    place_cluster_into_area,
    generate_conflict_report,
    create_area_aware_seating,
    split_oversized_families
)
from helpers_for_testing import make_family
from family import Family

# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------

@pytest.fixture
def simple_families():
    """
    Test fixture:
      - Smith1 requests Jones
      - Smith2 requests nobody
      - Jones requests nobody
    """
    smith1 = make_family("John", "Smith", 4)
    smith2 = make_family("Paul", "Smith", 3)
    jones  = make_family("Ava", "Jones", 2)

    request_map: Dict[Family, List[Family]] = {
        smith1: [jones],
        smith2: [],
        jones:  [],
    }

    families = [smith1, smith2, jones]
    return families, request_map, smith1, smith2, jones

@pytest.fixture
def complex_families():
    """
    Test fixture:
    """
    jones = make_family("Christopher", "Jones", 4)
    schrader = make_family("Terry", "Schrader", 3)
    brown  = make_family("Bill", "Brown", 2)
    clyde  = make_family("Tom", "Clyde", 2)
    bonnie = make_family("Tresa", "Bonnie", 4)
    meanie = make_family("Owen", "Meanie", 5)



    request_map: Dict[Family, List[Family]] = {
        jones: [schrader],
        schrader: [brown, schrader],
        brown:  [],
        clyde: [bonnie],
        bonnie: [],
        meanie: [],
    }

    families = [jones, schrader, brown, clyde, bonnie, meanie]
    return families, request_map, jones, schrader, brown, clyde, bonnie, meanie

# ---------------------------------------------------------
# 1. Test cluster building
# ---------------------------------------------------------

def test_build_clusters(simple_families):
    """
    Clusters should reflect connected components of the request graph.
    """
    families, request_map, smith1, smith2, jones = simple_families

    clusters = build_clusters(families, request_map)

    # smith1 ↔ jones form a cluster
    assert any(set(cluster) == {smith1, jones} for cluster in clusters)

    # smith2 stands alone
    assert any(cluster == [smith2] for cluster in clusters)

def test_build_complex_clusters(complex_families):
    """
    Clusters should reflect connected components of the request graph.
    """
    families, request_map, jones, schrader, brown, clyde, bonnie, meanie = complex_families

    clusters = build_clusters(families, request_map)

    # jones, schrader, brown cluster
    assert any(set(cluster) == {jones, schrader, brown} for cluster in clusters)
    # bonnie, clyde cluster
    assert any(set(cluster) == {bonnie, clyde} for cluster in clusters)
    # meanie stands alone
    assert any(cluster == [meanie] for cluster in clusters)

# ---------------------------------------------------------
# 2. Test cluster → area assignment
# ---------------------------------------------------------

def test_assign_cluster_to_area(simple_families):
    families, request_map, smith1, smith2, jones = simple_families

    areas: Dict[int, List[List[Family]]] = {}
    area_used: Dict[int, int] = {}

    # First cluster (smith1 + jones)
    cluster1 = [smith1, jones]
    area_idx = assign_cluster_to_area(cluster1, areas, area_used, table_size=10, debug=False)
    assert area_idx == 0

    # Simulate placement correctly: one table with the cluster
    areas[0] = [[smith1, jones]]
    area_used[0] = smith1.size + jones.size  # 6 seats used

    # Second cluster (smith2) should fit into area 0
    cluster2 = [smith2]
    area_idx2 = assign_cluster_to_area(cluster2, areas, area_used, table_size=10, debug=False)
    assert area_idx2 == 0

def test_two_large_clusters_create_two_areas():
    # Each cluster is size 12, table_size=10 → requires 2 tables
    # But areas start with 1 table → second cluster must go to new area
    c1 = [make_family("A1", "Alpha", 6), make_family("A2", "Alpha", 6)]
    c2 = [make_family("B1", "Beta", 7), make_family("B2", "Beta", 5)]

    families = c1 + c2
    request_map = {f: [] for f in families}

    areas, conflicts, layout = create_area_aware_seating(
        families_sorted=families,
        requests_map=request_map,
        table_size=10,
        debug=False,
    )

    assert len(areas) >= 2

def test_many_small_clusters_fill_multiple_areas():
    # 10 clusters of size 6 → each requires a new table
    families = [make_family(f"F{i}", f"L{i}", 6) for i in range(10)]
    request_map = {f: [] for f in families}

    areas, conflicts, layout = create_area_aware_seating(
        families_sorted=families,
        requests_map=request_map,
        table_size=10,
        debug=False,
    )

    # Each cluster requires a new table → each cluster must be a new area
    assert len(areas) >= 5

# ---------------------------------------------------------
# 3. Test table placement
# ---------------------------------------------------------

def test_place_cluster_into_area(simple_families):
    """
    Families in a cluster should be placed together when space allows.
    """
    families, request_map, smith1, smith2, jones = simple_families

    area_tables: List[List[Family]] = []
    place_cluster_into_area(
        [smith1, jones],
        area_tables,
        table_size=10,
        requests_map=request_map,
        debug=False,
    )

    assert area_tables[0] == [smith1, jones]


def test_place_cluster_creates_new_table(simple_families):
    """
    When a table cannot fit the next family, a new table should be created.
    """
    families, request_map, smith1, smith2, jones = simple_families

    area_tables: List[List[Family]] = []
    place_cluster_into_area(
        [smith1, smith2],
        area_tables,
        table_size=6,
        requests_map=request_map,
        debug=False,
    )

    assert area_tables[0] == [smith1]
    assert area_tables[1] == [smith2]


# ---------------------------------------------------------
# 4. Test conflict report
# ---------------------------------------------------------

def test_conflict_report(simple_families):
    """
    Conflicts should be reported when requested families are in different areas.
    """
    families, request_map, smith1, smith2, jones = simple_families

    areas = {
        0: [[smith1]],
        1: [[jones]],
    }

    conflicts = generate_conflict_report(areas, request_map)
    assert len(conflicts) == 1

    fam, other, reason = conflicts[0]
    assert fam == smith1
    assert other == jones
    assert reason == "Not seated in same area"


# ---------------------------------------------------------
# 5. Test full pipeline
# ---------------------------------------------------------

def test_full_pipeline(simple_families):
    """
    Full seating pipeline should:
      - keep clusters together
      - reuse areas efficiently
      - produce no conflicts when requests are satisfied
    """
    families, request_map, smith1, smith2, jones = simple_families

    areas, conflicts, layout = create_area_aware_seating(
        families_sorted=families,
        requests_map=request_map,
        table_size=10,
        debug=False,
    )

    # smith1 and jones should be in same area
    smith_area = next(a for a, tables in areas.items() if smith1 in sum(tables, []))
    jones_area = next(a for a, tables in areas.items() if jones in sum(tables, []))
    assert smith_area == jones_area

    # smith2 should also fit into area 0
    smith2_area = next(a for a, tables in areas.items() if smith2 in sum(tables, []))
    assert smith2_area == smith_area

    assert conflicts == []
    assert "Smith" in layout
    assert "Jones" in layout


# ---------------------------------------------------------
# 6. Additional thorough tests
# ---------------------------------------------------------

def test_oversized_family():
    """
    Families larger than table_size must be seated across multiple tables.
    For size=15 and table_size=10, the family should occupy 2 tables:
        - Table 0: 10 seats used
        - Table 1: 5 seats used
    The next family (size=2) should fit into the last table if space allows.
    """
    big = make_family("Big", "Family", 15)
    cluster = split_oversized_families([big], table_size=10, requests_map={})
    assert [f.size for f in cluster] == [10, 5]


def test_multiple_clusters_area_reuse():
    """
    Multiple clusters should pack into the same area when space allows.
    """
    a = make_family("A", "One", 4)
    b = make_family("B", "Two", 4)
    c = make_family("C", "Three", 4)

    request_map = {a: [], b: [], c: []}
    families = [a, b, c]

    areas, conflicts, _ = create_area_aware_seating(
        families_sorted=families,
        requests_map=request_map,
        table_size=10,
        debug=False,
    )

    # Since the third family is in a separate cluster and would require a new table,
    # it is put in a new area.
    assert len(areas) == 2
    assert conflicts == []


def test_requested_families_affect_table_choice():
    """
    Families should be placed near requested families when possible.
    """
    a = make_family("A", "One", 3)
    b = make_family("B", "Two", 3)
    c = make_family("C", "Three", 3)

    request_map = {
        a: [b],  # a wants to sit near b
        b: [],
        c: [],
    }

    # Pre-seat b at table 0
    area_tables = [[b]]

    place_cluster_into_area(
        [a, c],
        area_tables,
        table_size=10,
        requests_map=request_map,
        debug=False,
    )

    # a should join b
    assert a in area_tables[0]

    # c can go anywhere
    assert c in sum(area_tables, [])

def test_clusters_can_share_tables_when_space_allows():
    """
    Families from different clusters should be seated at the same table
    when there is sufficient space. This demonstrates the intended behavior
    of minimizing table count rather than isolating clusters.
    """

    # Cluster 1: Smith + Jones
    smith = make_family("John", "Smith", 3)
    jones = make_family("Ava", "Jones", 2)

    # Cluster 2: Brown (separate cluster)
    brown = make_family("Charlie", "Brown", 4)

    # Request map:
    #   Smith requests Jones → cluster 1
    #   Brown requests nobody → cluster 2
    request_map = {
        smith: [jones],
        jones: [],
        brown: [],
    }

    # Families sorted by submission time
    families = [smith, jones, brown]

    # Run the full seating pipeline
    areas, conflicts, _ = create_area_aware_seating(
        families_sorted=families,
        requests_map=request_map,
        table_size=10,   # Plenty of room for all three at one table
        debug=False,
    )

    # Extract the single area and its tables
    assert len(areas) == 1
    tables = list(areas.values())[0]

    # Flatten tables
    seated = sum(tables, [])

    # All three families should be at the same table
    assert smith in tables[0]
    assert jones in tables[0]
    assert brown in tables[0]

    # No conflicts expected
    assert conflicts == []

