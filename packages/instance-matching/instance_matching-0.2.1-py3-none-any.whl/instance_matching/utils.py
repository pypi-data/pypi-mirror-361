import numpy as np
from collections import defaultdict
from shapely.geometry import LineString
from scipy.spatial.distance import cdist

def interpolate_points(points, num_points):
    line = LineString(points)
    distances = np.linspace(0, line.length, num_points)
    return np.array([line.interpolate(d).coords[0] for d in distances])

def sample_linestring_with_noise(line: LineString, interval: float=0.2, noise_std: float=0.3, offset_std: float=0.3) -> LineString:
    total_length = line.length
    num_samples = max(int(np.floor(total_length / interval)) + 1, 2)

    distances = np.linspace(0, total_length, num_samples)
    
    random_offset_x = np.random.normal(0, offset_std)
    random_offset_y = np.random.normal(0, offset_std)
    sampled_coords = []
    for i, d in enumerate(distances):
        point = line.interpolate(d)
        x, y = point.x, point.y

        # if i != 0 and i != len(distances) - 1:
        #     x += (np.random.normal(0, noise_std) + random_offset_x)
        #     y += (np.random.normal(0, noise_std) + random_offset_y)
        x += (np.random.normal(0, noise_std) + random_offset_x)
        y += (np.random.normal(0, noise_std) + random_offset_y)

        sampled_coords.append((x, y))

    return LineString(sampled_coords)

def is_duplicate_edge(edges, edge, instance_type):
    if instance_type == 'center_lines':
        return edge in edges
    elif instance_type == 'lane_dividers':
        return edge in edges or (-edge[1], -edge[0]) in edges
    return False

def add_new_edge(edges, target_edge, instance_type):
    if not is_duplicate_edge(edges, target_edge, instance_type):
        edges.append(target_edge)
    return edges

def sample_edge(edges, target_idxs, instance_type):
    # Sample edges based on the target idxs
    target_set = set(target_idxs)
    if instance_type == 'center_lines':
        return [(x, y) for (x, y) in edges if x in target_set and y in target_set]
    elif instance_type == 'lane_dividers':
        filtered = []
        for x, y in edges:
            if (x in target_set and y in target_set):
                filtered.append((x, y))
            elif (-y in target_set and -x in target_set):
                filtered.append((-y, -x))
        return filtered

def get_lane_divder_instance_from_idx(instance_idxs, instance_pts, idx):
    rel_idxs = np.where(np.array(instance_idxs) == idx)[0]
    if len(rel_idxs) > 0:
        return [instance_pts[i] for i in rel_idxs]
    else:
        return [None]
    
def lane_divider_connection_check(from_instance, to_instance, from_instance_idx, to_instance_idx, instance_idxs):
    # Return format: valid_connection, from_instance inversion flag, to_instance inversion flag
    # For inversion flag, it is set as True, if the instance is inverted
    if from_instance_idx in instance_idxs and to_instance_idx in instance_idxs:
        from_first_point = np.array(from_instance.coords[0])
        from_last_point = np.array(from_instance.coords[-1])
        to_first_point = np.array(to_instance.coords[0])
        to_last_point = np.array(to_instance.coords[-1])

        from_pts = np.array(from_instance.coords)
        to_pts = np.array(to_instance.coords)
        dists = cdist(from_pts, to_pts)
        min_dist = np.min(dists)

        if min_dist < 1e0: # Two instances are physically in contact

            d11 = np.linalg.norm(from_last_point - to_first_point) # (normal) - (normal)
            d12 = np.linalg.norm(from_last_point - to_last_point) # (normal) - (inverted)
            d21 = np.linalg.norm(from_first_point - to_first_point) # (inverted) - (normal)
            d22 = np.linalg.norm(from_first_point - to_last_point) # (inverted) - (inverted)
            idx = np.argmax(np.array([d11, d12, d21, d22]))

            if idx == 0:
                return True, False, False
            elif idx == 1:
                return True, False, True
            elif idx == 2:
                return True, True, False
            elif idx == 3:
                return True, True, True
        else:
            return False, None, None
    else:
        return False, None, None    

def convert_global_to_local(edges, idxs, pts):
    # First index is not 0, but 1! 
    # This is to preserve the edge direction of the first instance
    # -0 = 0 (ambiguous edge direction)
    local_edges = []
    idxs = np.array(idxs)
    
    # index map to avoid repeated np.where
    idx_to_locals = defaultdict(list)
    for i, idx in enumerate(idxs):
        idx_to_locals[idx].append(i)

    for from_idx, to_idx in edges:
        abs_from, abs_to = abs(from_idx), abs(to_idx)
        from_candidates = idx_to_locals[abs_from]
        to_candidates = idx_to_locals[abs_to]

        if len(from_candidates) == 1 and len(to_candidates) == 1:
            from_local = from_candidates[0] + 1
            to_local = to_candidates[0] + 1
        else:
            from_points = np.array([
                pts[i].coords[0] if from_idx < 0 else pts[i].coords[-1]
                for i in from_candidates
            ])
            to_points = np.array([
                pts[i].coords[-1] if to_idx < 0 else pts[i].coords[0]
                for i in to_candidates
            ])
            D = cdist(from_points, to_points)
            row, col = np.unravel_index(np.argmin(D), D.shape)
            from_local = from_candidates[row] + 1
            to_local = to_candidates[col] + 1

        local_edges.append((
            -from_local if from_idx < 0 else from_local,
            -to_local if to_idx < 0 else to_local
        ))

    return local_edges
