from collections import defaultdict, deque

# ---------------------------------------------------------
# 1. BUILD CLUSTERS
# ---------------------------------------------------------

def build_clusters(families, requests_map):
    graph = defaultdict(set)

    # Build edges
    for fam in families:
        reqs = requests_map.get(fam, [])
        for other in families:
            if other.last_name in reqs:
                graph[fam].add(other)
                graph[other].add(fam)

    visited = set()
    clusters = []

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


# ---------------------------------------------------------
# 2. ASSIGN CLUSTERS TO AREAS (NO BALANCING)
# ---------------------------------------------------------

def assign_clusters_to_areas(clusters, tables_per_area, table_size, debug=True):
    """
    Areas are created only when needed.
    No balancing logic.
    """
    areas = []
    area_capacity = []  # total seats used per area

    for cluster in clusters:
        cluster_size = sum(f.size for f in cluster)
        total_capacity = tables_per_area * table_size

        if debug:
            print(f"\n=== Assigning cluster {[f.name for f in cluster]} (size {cluster_size}) ===")

        # Try to place cluster in any existing area with enough total capacity
        placed = False
        for i, used in enumerate(area_capacity):
            if used + cluster_size <= total_capacity:
                if debug:
                    print(f"Placing cluster in existing Area {i}")
                area_capacity[i] += cluster_size
                yield ("existing", i, cluster)
                placed = True
                break

        # Otherwise create a new area
        if not placed:
            new_area_index = len(areas)
            if debug:
                print(f"Creating NEW Area {new_area_index} for cluster")
            areas.append([])
            area_capacity.append(cluster_size)
            yield ("new", new_area_index, cluster)


# ---------------------------------------------------------
# 3. PLACE CLUSTER INTO AREA TABLES
# ---------------------------------------------------------

def place_cluster_into_area(cluster, area_tables, table_size, tables_per_area, debug=True):
    if not area_tables:
        area_tables.extend([[] for _ in range(tables_per_area)])

    table_used = [sum(f.size for f in table) for table in area_tables]

    for fam in cluster:
        if debug:
            print(f"  Placing family {fam.name} (size {fam.size})")

        # Try to place near requested families
        best_table = None
        best_score = -1

        for i, table in enumerate(area_tables):
            score = sum(1 for f in table if f.last_name in fam.requests)
            if table_used[i] + fam.size <= table_size and score > best_score:
                best_score = score
                best_table = i

        if best_table is not None:
            if debug:
                print(f"    → Placed at Table {best_table} (matched {best_score} requested families)")
            area_tables[best_table].append(fam)
            table_used[best_table] += fam.size
            continue

        # Otherwise place in first table with space
        for i, used in enumerate(table_used):
            if used + fam.size <= table_size:
                if debug:
                    print(f"    → No request matches; placed at first available Table {i}")
                area_tables[i].append(fam)
                table_used[i] += fam.size
                break


# ---------------------------------------------------------
# 4. CONFLICT REPORT
# ---------------------------------------------------------

def generate_conflict_report(areas, requests_map):
    conflicts = []

    # Build lookup: family → (area, table)
    location = {}
    for area_idx, tables in areas.items():
        for table_idx, table in enumerate(tables):
            for fam in table:
                location[fam] = (area_idx, table_idx)

    # Check each family's requests
    for fam, reqs in requests_map.items():
        fam_area, fam_table = location.get(fam, (None, None))

        for other_last in reqs:
            matches = [f for f in location if f.last_name == other_last]

            if not matches:
                conflicts.append((fam, other_last, "Requested family not found"))
                continue

            satisfied = False
            for other in matches:
                o_area, o_table = location[other]
                if fam_area == o_area:
                    satisfied = True
                    break

            if not satisfied:
                conflicts.append((fam, other_last, "Not seated in same area"))

    return conflicts


# ---------------------------------------------------------
# 5. VISUALIZATION
# ---------------------------------------------------------

def visualize_areas(areas):
    output = []
    for area_idx, tables in areas.items():
        output.append(f"\n==================== AREA {area_idx} ====================")
        for t_idx, table in enumerate(tables):
            output.append(f"  Table {t_idx}:")
            for fam in table:
                output.append(f"    - {fam.name} ({fam.size})")
    return "\n".join(output)


# ---------------------------------------------------------
# 6. FULL PIPELINE
# ---------------------------------------------------------

def create_area_aware_seating(families_sorted, requests_map, table_size=10, tables_per_area=3, debug=True):
    if debug:
        print("\n==================== BUILDING CLUSTERS ====================")

    clusters = build_clusters(families_sorted, requests_map)

    clusters.sort(key=lambda c: families_sorted.index(c[0]))

    if debug:
        print("\n==================== ASSIGNING CLUSTERS TO AREAS ====================")

    areas = defaultdict(list)

    for action, area_index, cluster in assign_clusters_to_areas(
        clusters, tables_per_area, table_size, debug
    ):
        if debug:
            print(f"→ Cluster {[f.name for f in cluster]} assigned to Area {area_index}")

        place_cluster_into_area(cluster, areas[area_index], table_size, tables_per_area, debug)

    # Conflict report
    conflicts = generate_conflict_report(areas, requests_map)

    # Visualization
    layout = visualize_areas(areas)

    return areas, conflicts, layout

