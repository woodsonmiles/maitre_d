"""
seating_chart.py

Core seating engine for assigning families to tables and areas.

Architecture:
------------
1. seating_requests.py parses messy human text into:
       Dict[Family, List[Family]]
   (explicit, unambiguous request graph).

2. seating_chart.py receives that graph and:
   - Builds clusters (connected components)
   - Assigns clusters to areas (cluster-level bin packing)
   - Places families into tables (family-level bin packing)
   - Generates conflict reports
   - Produces a human-readable layout
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, List, Tuple, DefaultDict
import math
from math import ceil
from family import Family


# You have a concrete Family class elsewhere; we just rely on its interface:
# - first_name: str
# - last_name: str
# - size: int
# - to_dict(): dict


# =========================================================
# 1. BUILD CLUSTERS (CONNECTED COMPONENTS)
# =========================================================

def build_clusters(
    families: List["Family"],
    requests_map: Dict["Family", List["Family"]],
) -> List[List["Family"]]:
    """
    Build clusters of families based on explicit Family → List[Family] requests.

    A cluster is a connected component in the undirected graph where:
        - Nodes are Family objects
        - Edges exist if A requests B or B requests A
    """
    graph: DefaultDict["Family", set["Family"]] = defaultdict(set)

    # Build undirected edges
    for fam in families:
        for other in requests_map.get(fam, []):
            graph[fam].add(other)
            graph[other].add(fam)

    visited: set["Family"] = set()
    clusters: List[List["Family"]] = []

    # BFS to find connected components
    for fam in families:
        if fam in visited:
            continue

        queue: deque["Family"] = deque([fam])
        visited.add(fam)
        cluster: List["Family"] = [fam]

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

def assign_cluster_to_area(
    cluster: List["Family"],
    areas: Dict[int, List[List["Family"]]],
    area_used: Dict[int, int],
    table_size: int,
    debug: bool = True,
) -> int:
    """
    Decide which area a cluster should be placed into.
    If placing a cluster requires creating a new table in an existing area, put it in a new area instead.

    Returns:
        area_index (int)
    """
    cluster_size = sum(f.size for f in cluster)

    if debug:
        print(
            f"\n=== Deciding area for cluster {[f.last_name for f in cluster]} "
            f"(size {cluster_size}) ==="
        )

    best_area: int | None = None
    best_extra: float | None = None
    best_remaining: int | None = None

    # Evaluate existing areas
    for area_idx, tables in areas.items():
        num_tables = len(tables)
        used = area_used.get(area_idx, 0)
        capacity = num_tables * table_size
        remaining = capacity - used

        if remaining >= cluster_size:
            extra = 0
        else:
            # This area cannot accept the cluster without adding tables
            extra = float("inf")

        if debug:
            print(
                f"  Area {area_idx}: tables={num_tables}, used={used}, "
                f"remaining={remaining}, extra_tables_needed={extra}"
            )

        if best_extra is None or extra < best_extra:
            best_area = area_idx
            best_extra = extra
            best_remaining = remaining
        elif extra == best_extra and best_remaining is not None and remaining > best_remaining:
            best_area = area_idx
            best_remaining = remaining

    # Consider creating a new area
    new_area_idx = len(areas)
    extra_new = math.ceil(cluster_size / table_size)

    if debug:
        print(f"  New Area {new_area_idx}: extra_tables_needed={extra_new}")

    if best_area is None or extra_new < best_extra:  # type: ignore[arg-type]
        if debug:
            print(f"→ Choosing NEW Area {new_area_idx}")
        return new_area_idx

    if debug:
        print(f"→ Choosing EXISTING Area {best_area}")
    return best_area  # type: ignore[return-value]


# =========================================================
# 3. PLACE CLUSTER INTO AREA TABLES (FAMILY-LEVEL BIN PACKING)
# =========================================================

def place_cluster_into_area(
    cluster: List["Family"],
    area_tables: List[List["Family"]],
    table_size: int,
    requests_map: Dict["Family", List["Family"]],
    debug: bool = True,
) -> None:
    """
    Place all families in a (possibly split) cluster into tables.

    Since oversized families have already been split into table-sized chunks,
    this function becomes a pure bin-packing routine with adjacency scoring.
    """
    if debug:
        print(f"  Placing cluster of {len(cluster)} families")

    # Track used seats per table
    table_used = [sum(f.size for f in table) for table in area_tables]

    for fam in cluster:
        if debug:
            print(f"    Placing {fam.last_name} (size {fam.size}, part={fam.part})")

        requested = set(requests_map.get(fam, []))

        best_table = None
        best_score = -1

        # Try to place near requested families
        for i, table in enumerate(area_tables):
            remaining = table_size - table_used[i]
            if remaining < fam.size:
                continue

            score = sum(1 for other in table if other in requested)

            if score > best_score:
                best_score = score
                best_table = i

        if best_table is not None:
            if debug:
                print(f"      → Placed at table {best_table} (score {best_score})")
            area_tables[best_table].append(fam)
            table_used[best_table] += fam.size
            continue

        # Otherwise place in first table with space
        placed = False
        for i, used in enumerate(table_used):
            if used + fam.size <= table_size:
                if debug:
                    print(f"      → Placed at table {i} (first fit)")
                area_tables[i].append(fam)
                table_used[i] += fam.size
                placed = True
                break

        # If no table fits, create a new one
        if not placed:
            new_idx = len(area_tables)
            if debug:
                print(f"      → Created new table {new_idx}")
            area_tables.append([fam])
            table_used.append(fam.size)

# split families bigger than tables into multiple families in the same cluster of requests
def split_oversized_families(
    cluster: List["Family"],
    table_size: int,
    requests_map: Dict["Family", List["Family"]],
) -> List["Family"]:
    """
    Replace any oversized families in the cluster with multiple sub-families
    whose sizes do not exceed table_size.

    Each sub-family:
      - has the same first/last name
      - has a unique `part` index (0, 1, 2, ...)
      - inherits the original family's requests
      - stays in the same cluster

    Returns:
        A new list of Family objects (original or split).
    """
    new_cluster: List["Family"] = []

    for fam in cluster:
        if fam.size <= table_size:
            # Normal family, keep as-is
            new_cluster.append(fam)
            continue

        # Oversized family → split into parts
        parts_needed = ceil(fam.size / table_size)
        remaining = fam.size

        for part_idx in range(parts_needed):
            part_size = min(table_size, remaining)
            remaining -= part_size

            # Create a new Family object with part index
            fam_part = Family(
                email=fam.email,
                phone=fam.phone,
                address=fam.address,
                requests=fam.requests,
                submission=fam.submission,
                guests=fam.guests[:part_size],  # or generate placeholder guests
                part=part_idx,
            )

            new_cluster.append(fam_part)

            # Propagate requests: each sub-family inherits the same request list
            requests_map[fam_part] = requests_map.get(fam, [])

    return new_cluster

# =========================================================
# 4. CONFLICT REPORT
# =========================================================

def generate_conflict_report(
    areas: Dict[int, List[List["Family"]]],
    requests_map: Dict["Family", List["Family"]],
) -> List[Tuple["Family", "Family", str]]:
    """
    Generate a list of unmet seating requests.

    A request is satisfied if the requested family is seated in the same AREA.
    """
    conflicts: List[Tuple["Family", "Family", str]] = []

    # Build lookup: family → (area, table)
    location: Dict["Family", Tuple[int, int]] = {}
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

def visualize_areas(areas: Dict[int, List[List["Family"]]]) -> str:
    """
    Produce a human-readable string representation of areas and tables.
    """
    output: List[str] = []
    for area_idx, tables in areas.items():
        output.append(f"\n==================== AREA {area_idx} ====================")
        for t_idx, table in enumerate(tables):
            output.append(f"  Table {t_idx}:")
            for fam in table:
                output.append(
                    f"    - {fam.first_name} {fam.last_name} (size {fam.size})"
                )
    return "\n".join(output)

def visualize_clusters(clusters: list[list["Family"]]) -> None:
    """
    Pretty-print clusters when debug mode is enabled.
    Each cluster is shown with its families, including part numbers.
    """
    print("\n=== CLUSTERS ===")
    for idx, cluster in enumerate(clusters):
        print(f"Cluster {idx} ({len(cluster)} families):")
        for fam in cluster:
            part = getattr(fam, "part", 0)
            if part:
                print(f"  - {fam.first_name} {fam.last_name} (size={fam.size}, part={part})")
            else:
                print(f"  - {fam.first_name} {fam.last_name} (size={fam.size})")
        print()
    print("================\n")



# =========================================================
# 6. FULL PIPELINE
# =========================================================

def create_area_aware_seating(
    families_sorted: List["Family"],
    requests_map: Dict["Family", List["Family"]],
    table_size: int = 10,
    debug: bool = True,
) -> Tuple[Dict[int, List[List["Family"]]], List[Tuple["Family", "Family", str]], str]:
    """
    Full seating pipeline.

    Returns:
        areas: Dict[int, List[List[Family]]]
        conflicts: List[(Family, Family, str)]
        layout: str
    """
    print("\n==================== CLUSTERS ====================")

    clusters = build_clusters(families_sorted, requests_map)
    visualize_clusters(clusters)

    # Keep cluster order consistent with original family order
    clusters.sort(key=lambda c: families_sorted.index(c[0]))

    print("\n==================== AREAS ====================")

    areas: DefaultDict[int, List[List["Family"]]] = defaultdict(list)
    area_used: Dict[int, int] = defaultdict(int)

    for cluster in clusters:
        area_idx = assign_cluster_to_area(
            cluster, areas, area_used, table_size, debug
        )

        if debug:
            print(
                f"→ Cluster {[f.last_name for f in cluster]} "
                f"assigned to Area {area_idx}"
            )

        place_cluster_into_area(
            cluster,
            areas[area_idx],
            table_size,
            requests_map=requests_map,
            debug=debug,
        )

        area_used[area_idx] += sum(f.size for f in cluster)

    if debug:
        print("\n==================== GENERATING CONFLICT REPORT ====================")

    conflicts = generate_conflict_report(areas, requests_map)

    if debug:
        print("\n==================== FINAL LAYOUT ====================")

    layout = visualize_areas(areas)

    return areas, conflicts, layout
