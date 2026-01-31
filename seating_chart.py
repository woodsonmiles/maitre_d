"""
seating_chart.py

Core seating engine for assigning families to tables and areas.

Architecture:
------------
1. seating_requests.py parses messy human text into:
       Family → List[Family]
   This is the ONLY place where fuzzy matching or heuristics occur.

2. seating_chart.py receives a clean, unambiguous request graph and:
   - Builds clusters (connected components)
   - Assigns clusters to areas (cluster-level bin packing)
   - Places families into tables (family-level bin packing)
   - Generates conflict reports
   - Produces a human-readable layout

This file contains NO fuzzy matching, NO string parsing, and NO heuristics.
It operates purely on Family objects and explicit relationships.
"""

from collections import defaultdict, deque
import math


# =========================================================
# 1. BUILD CLUSTERS (CONNECTED COMPONENTS)
# =========================================================

def build_clusters(families, requests_map):
    """
    Build clusters of families based on explicit Family → List[Family] requests.

    A cluster is a connected component in the undirected graph where:
        - Nodes are Family objects
        - Edges exist if A requests B or B requests A

    Parameters:
        families: List[Family]
        requests_map: Dict[Family, List[Family]]

    Returns:
        List[List[Family]] — each inner list is a cluster
    """
    graph = defaultdict(set)

    # Build undirected edges
    for fam in families:
        for other in requests_map.get(fam, []):
            graph[fam].add(other)
            graph[other].add(fam)

    visited = set()
    clusters = []

    # BFS to find connected components
    for fam in families:
        if fam in visited:
            continue

        queue = deque([fam])
        visited.add(fam)
        cluster = [fam]

        while queue:
            cur = queue.popleft()
            for neighbor in graph[cur]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    cluster.append(neighbor)

        clusters.append(cluster)

    return clusters


# =========================================================
# 2. ASSIGN CLUSTERS TO AREAS (CLUSTER-LEVEL BIN PACKING)
# =========================================================

def assign_cluster_to_area(cluster, areas, area_used, table_size, debug=True):
    """
    Decide which area a cluster should be placed into.

    Returns:
        area_index (int)
    """
    cluster_size = sum(f.size for f in cluster)

    if debug:
        print(
            f"\n=== Deciding area for cluster {[f.last_name for f in cluster]} "
            f"(size {cluster_size}) ==="
        )

    best_area = None
    best_extra = None
    best_remaining = None

    # Evaluate existing areas
    for area_idx, tables in areas.items():
        num_tables = len(tables)
        used = area_used[area_idx]
        capacity = num_tables * table_size
        remaining = capacity - used

        if remaining >= cluster_size:
            extra = 0
        else:
            extra = math.ceil((cluster_size - remaining) / table_size)

        if best_extra is None or extra < best_extra:
            best_area = area_idx
            best_extra = extra
            best_remaining = remaining
        elif extra == best_extra and remaining > best_remaining:
            best_area = area_idx
            best_remaining = remaining

    # Consider creating a new area
    new_area_idx = len(areas)
    extra_new = math.ceil(cluster_size / table_size)

    if best_area is None or extra_new < best_extra:
        if debug:
            print(f"→ Choosing NEW Area {new_area_idx}")
        return new_area_idx

    if debug:
        print(f"→ Choosing EXISTING Area {best_area}")
    return best_area

# =========================================================
# 3. PLACE CLUSTER INTO AREA TABLES (FAMILY-LEVEL BIN PACKING)
# =========================================================

def place_cluster_into_area(cluster, area_tables, table_size, debug=True):
    """
    Place all families in a cluster into the tables of a given area.

    Rules:
    ------
    - Families must NOT be split across tables unless size > table_size.
    - Try to reuse existing tables when possible.
    - Prefer tables that already contain requested families.
    - Create new tables only when necessary.

    Parameters:
        cluster: List[Family]
        area_tables: List[List[Family]]
        table_size: int
    """
    if not area_tables:
        area_tables.append([])

    table_used = [sum(f.size for f in table) for table in area_tables]

    for fam in cluster:
        if debug:
            print(
                f"  Placing family {fam.first_name} {fam.last_name} "
                f"(size {fam.size})"
            )

        # Oversized family (rare)
        if fam.size > table_size:
            if debug:
                print(
                    f"    WARNING: family size {fam.size} exceeds table_size "
                    f"{table_size}; placing at its own table."
                )
            area_tables.append([fam])
            table_used.append(fam.size)
            continue

        # Try to place near requested families
        best_table = None
        best_score = -1

        for i, table in enumerate(area_tables):
            remaining = table_size - table_used[i]
            if remaining < fam.size:
                continue

            score = sum(1 for other in table if other in fam.requests)

            if score > best_score:
                best_score = score
                best_table = i

        if best_table is not None:
            if debug:
                print(
                    f"    → Placed at Table {best_table} "
                    f"(matched {best_score} requested families)"
                )
            area_tables[best_table].append(fam)
            table_used[best_table] += fam.size
            continue

        # Otherwise place in first table with space
        placed = False
        for i, used in enumerate(table_used):
            if used + fam.size <= table_size:
                if debug:
                    print(f"    → No request matches; placed at Table {i}")
                area_tables[i].append(fam)
                table_used[i] += fam.size
                placed = True
                break

        # If no table fits, create a new one
        if not placed:
            new_idx = len(area_tables)
            if debug:
                print(f"    → No table had space; created new Table {new_idx}")
            area_tables.append([fam])
            table_used.append(fam.size)


# =========================================================
# 4. CONFLICT REPORT
# =========================================================

def generate_conflict_report(areas, requests_map):
    """
    Generate a list of unmet seating requests.

    A request is satisfied if:
        - The requested family is seated in the same AREA.

    Returns:
        List[(fam, requested_fam, reason)]
    """
    conflicts = []

    # Build lookup: family → (area, table)
    location = {}
    for area_idx, tables in areas.items():
        for table_idx, table in enumerate(tables):
            for fam in table:
                location[fam] = (area_idx, table_idx)

    for fam, reqs in requests_map.items():
        fam_area = location.get(fam, (None, None))[0]

        for other in reqs:
            if other not in location:
                conflicts.append((fam, other, "Requested family not found"))
                continue

            other_area = location[other][0]
            if other_area != fam_area:
                conflicts.append((fam, other, "Not seated in same area"))

    return conflicts


# =========================================================
# 5. VISUALIZATION
# =========================================================

def visualize_areas(areas):
    """
    Produce a human-readable string representation of areas and tables.
    """
    output = []
    for area_idx, tables in areas.items():
        output.append(f"\n==================== AREA {area_idx} ====================")
        for t_idx, table in enumerate(tables):
            output.append(f"  Table {t_idx}:")
            for fam in table:
                output.append(
                    f"    - {fam.first_name} {fam.last_name} (size {fam.size})"
                )
    return "\n".join(output)


# =========================================================
# 6. FULL PIPELINE
# =========================================================

def create_area_aware_seating(
    families_sorted,
    requests_map,
    table_size=10,
    debug=True,
):
    """
    Full seating pipeline.

    Steps:
    ------
    1. Build clusters (connected components).
    2. Sort clusters by first appearance in families_sorted.
    3. For each cluster:
         - Choose an area (cluster-level bin packing).
         - Place families into tables (family-level bin packing).
    4. Generate conflict report.
    5. Produce layout.

    Returns:
        areas, conflicts, layout
    """
    if debug:
        print("\n==================== BUILDING CLUSTERS ====================")

    clusters = build_clusters(families_sorted, requests_map)

    clusters.sort(key=lambda c: families_sorted.index(c[0]))

    if debug:
        print("\n==================== ASSIGNING CLUSTERS TO AREAS ====================")

    areas = defaultdict(list)
    area_used = defaultdict(int)

    for cluster in clusters:
        area_idx = assign_cluster_to_area(
            cluster, areas, area_used, table_size, debug
        )

        if debug:
            print(
                f"→ Cluster {[f.last_name for f in cluster]} "
                f"assigned to Area {area_idx}"
            )

        place_cluster_into_area(cluster, areas[area_idx], table_size, debug)

        area_used[area_idx] += sum(f.size for f in cluster)

    if debug:
        print("\n==================== GENERATING CONFLICT REPORT ====================")

    conflicts = generate_conflict_report(areas, requests_map)

    if debug:
        print("\n==================== FINAL LAYOUT ====================")

    layout = visualize_areas(areas)

    return areas, conflicts, layout
