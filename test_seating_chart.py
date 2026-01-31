import pytest
from seating_chart import (
    build_clusters,
    assign_cluster_to_area,
    place_cluster_into_area,
    generate_conflict_report,
    create_area_aware_seating,
)

# ---------------------------------------------------------
# Minimal mock Family class for testing
# ---------------------------------------------------------

class MockFamily:
    def __init__(self, first, last, size=1, requests=None):
        self._first = first
        self._last = last
        self._size = size
        self.requests = requests or []  # list[Family]
    @property
    def first_name(self):
        return self._first
    @property
    def last_name(self):
        return self._last
    @property
    def size(self):
        return self._size
    def __repr__(self):
        return f"Family({self._first} {self._last}, size={self._size})"


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------

@pytest.fixture
def simple_families():
    """
    Smith1 requests Jones.
    Smith2 requests nobody.
    Jones requests nobody.
    """
    smith1 = MockFamily("John", "Smith", size=4)
    smith2 = MockFamily("Paul", "Smith", size=3)
    jones  = MockFamily("Ava", "Jones", size=2)

    # Explicit Family → List[Family] mapping
    smith1.requests = [jones]
    smith2.requests = []
    jones.requests  = []

    families = [smith1, smith2, jones]
    request_map = {
        smith1: [jones],
        smith2: [],
        jones:  [],
    }
    return families, request_map, smith1, smith2, jones


# ---------------------------------------------------------
# 1. Test cluster building
# ---------------------------------------------------------

def test_build_clusters(simple_families):
    families, request_map, smith1, smith2, jones = simple_families

    clusters = build_clusters(families, request_map)

    # smith1 ↔ jones form a connected component
    assert any(set(cluster) == {smith1, jones} for cluster in clusters)

    # smith2 is isolated
    assert any(cluster == [smith2] for cluster in clusters)


# ---------------------------------------------------------
# 2. Test cluster → area assignment
# ---------------------------------------------------------

def test_assign_cluster_to_area(simple_families):
    families, request_map, smith1, smith2, jones = simple_families

    areas = {}
    area_used = {}

    # First cluster (smith1 + jones)
    cluster1 = [smith1, jones]
    area_idx = assign_cluster_to_area(cluster1, areas, area_used, table_size=10, debug=False)
    assert area_idx == 0

    # Add the area to simulate placement
    areas[0] = []
    area_used[0] = smith1.size + jones.size  # 6 seats used

    # Second cluster (smith2) should fit into area 0 (remaining 4 seats)
    cluster2 = [smith2]
    area_idx2 = assign_cluster_to_area(cluster2, areas, area_used, table_size=10, debug=False)
    assert area_idx2 == 0


# ---------------------------------------------------------
# 3. Test table placement
# ---------------------------------------------------------

def test_place_cluster_into_area(simple_families):
    families, request_map, smith1, smith2, jones = simple_families

    area_tables = []
    place_cluster_into_area([smith1, jones], area_tables, table_size=10, debug=False)

    # smith1 (4) + jones (2) fit at same table
    assert area_tables[0] == [smith1, jones]


def test_place_cluster_creates_new_table(simple_families):
    families, request_map, smith1, smith2, jones = simple_families

    area_tables = []
    # smith1 (4) + smith2 (3) fit at table 0
    place_cluster_into_area([smith1, smith2], area_tables, table_size=6, debug=False)

    # smith1 (4) fits, smith2 (3) does not → new table
    assert area_tables[0] == [smith1]
    assert area_tables[1] == [smith2]


# ---------------------------------------------------------
# 4. Test conflict report
# ---------------------------------------------------------

def test_conflict_report(simple_families):
    families, request_map, smith1, smith2, jones = simple_families

    # smith1 requests jones, but they are in different areas
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

    # smith2 should also fit into area 0 (remaining space)
    smith2_area = next(a for a, tables in areas.items() if smith2 in sum(tables, []))
    assert smith2_area == smith_area

    # No conflicts expected
    assert conflicts == []

    # Layout should contain names
    assert "Smith" in layout
    assert "Jones" in layout
