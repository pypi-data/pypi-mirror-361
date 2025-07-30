import numpy as np
from typing import Any, Dict, Iterable, Tuple

from shapely.geometry import LineString

from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment


def one_way_chamfer_distance(
    line1: LineString, 
    line2: LineString
) -> float:
    # Note that this is a one-way chamfer distance
    # Chamfer distance is computed with respect to the shorter linestring
    pts1 = np.array(line1.coords)
    pts2 = np.array(line2.coords)

    if line1.length <=  line2.length:
        src_pts = pts1
        tgt_pts = pts2
    else:
        src_pts = pts2
        tgt_pts = pts1

    dists = cdist(src_pts, tgt_pts)
    return np.mean(np.min(dists, axis=1))

def two_way_chamfer_distance(
    line1: LineString,
    line2: LineString
) -> float:
    """
    Compute Two-Way Chamfer Distance
    CD(line1, line2) = mean_{p1 in line1} min_{p2 in line2} ||p1 - p2|| +
                    mean_{p2 in line2} min_{p1 in line1} ||p2 - p1||
    """
    pts1 = np.array(line1.coords)
    pts2 = np.array(line2.coords)

    dists_12 = cdist(pts1, pts2)  # shape: (len(pts1), len(pts2))
    dists_21 = dists_12.T         # shape: (len(pts2), len(pts1))

    chamfer_12 = np.mean(np.min(dists_12, axis=1))  # line1 → line2
    chamfer_21 = np.mean(np.min(dists_21, axis=1))  # line2 → line1

    return chamfer_12 + chamfer_21

def build_adjacency_matrix(
    edges: Iterable[Tuple[int, int]],
    n_nodes: int,
    symmetric: bool = False
) -> np.ndarray:
    """
    Build an adjacency matrix from a list of edges.

    Args:
        edges: Iterable of (u, v) tuples.  Each u, v is a 1-based index (signed to indicate orientation).
        n_nodes: Number of nodes (including the padding “dummy” node if you’re using one-based with a dummy at the end).
        symmetric: If True, also set the reverse entry (v→u) to 1.

    Returns:
        A: (n_nodes × n_nodes) numpy array of 0/1 entries, where A[i, j] = 1 if there’s an edge
           from node (i+1) to node (j+1).
    """
    A = np.zeros((n_nodes, n_nodes), dtype=int)
    for u, v in edges:
        # convert 1-based signed indices to 0-based absolute indices
        i = abs(u) - 1
        j = abs(v) - 1
        A[i, j] = 1
        if symmetric:
            A[j, i] = 1
    return A

def build_cross_adjacency_matrix(
    center_instances: Dict[str, Any],
    lane_instances: Dict[str, Any]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build left- and right- cross-adjacency matrices between center-lines and lane-dividers.

    Each center-line has an associated left and right lane-divider index.
    We produce two binary matrices:
      - A_left[i, j] = 1 if center i connects to lane-divider j on its left
      - A_right[i, j] = 1 if center i connects to lane-divider j on its right

    Both matrices include one extra “dummy” row and column for padding:
      shape = (n_centers+1) × (n_lanes+1)

    Args:
        center_instances: dict containing at least:
            'idxs'             : List[int]    (1-based GT IDs of each center-line)
            'left_lane_idxs'   : List[int]    (1-based GT ID of the left divider for each center)
            'right_lane_idxs'  : List[int]    (1-based GT ID of the right divider for each center)
        lane_instances:   dict containing at least:
            'idxs'             : List[int]    (1-based GT IDs of each lane-divider)

    Returns:
        A_left, A_right: two numpy arrays of shape (n_centers+1, n_lanes+1)
    """
    # number of true segments
    nC = len(center_instances['idxs'])
    nL = len(lane_instances['idxs'])

    # initialize with padding row/col
    A_left  = np.zeros((nC+1, nL+1), dtype=int)
    A_right = np.zeros((nC+1, nL+1), dtype=int)

    # build a quick map from GT ID to local index
    lane_id_to_loc = {idx: loc for loc, idx in enumerate(lane_instances['idxs'])}

    # for each center-line instance
    for i, cen_id in enumerate(center_instances['idxs']):
        # left connection
        left_id = center_instances['left_lane_idxs'][i]
        j = lane_id_to_loc.get(left_id)
        if j is not None:
            A_left[i, j] = 1

        # right connection
        right_id = center_instances['right_lane_idxs'][i]
        j = lane_id_to_loc.get(right_id)
        if j is not None:
            A_right[i, j] = 1

    return A_left, A_right

def compute_gt_edges(
    idxs_map: np.ndarray,
    idxs_in:  np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build ground-truth mapping edges arrays between two index lists.

    Given:
      - idxs_map: 1D array of length M of 1-based GT IDs present in the existing map view.
      - idxs_in:  1D array of length N of 1-based GT IDs present in the input observations.

    Returns:
      - map2input_edges:  (M×2) array, where each row [i, j] means map-instance i → input-instance j,
                          or j = -1 if no match in `idxs_in`.
      - input2map_edges:  (N×2) array, where each row [i, j] means input-instance i → map-instance j,
                          or j = -1 if no match in `idxs_map`.
    """
    M = len(idxs_map)
    N = len(idxs_in)

    # initialize all links to “unmatched” (-1)
    map2input = np.full((M, 2), -1, dtype=int)
    input2map = np.full((N, 2), -1, dtype=int)

    # first column is the 0-based local index
    map2input[:, 0] = np.arange(M, dtype=int)
    input2map[:, 0] = np.arange(N, dtype=int)

    # fill in the matching column if global IDs align
    for i, mid in enumerate(idxs_map):
        # find any identical ID in the input list
        matches = np.where(idxs_in == mid)[0]
        if matches.size:
            map2input[i, 1] = matches[0]

    for j, iid in enumerate(idxs_in):
        matches = np.where(idxs_map == iid)[0]
        if matches.size:
            input2map[j, 1] = matches[0]

    return map2input, input2map

def to_gt_format(X: np.ndarray) -> np.ndarray:
    """
    Convert a continuous matching matrix into discrete map↔input edge lists via the Hungarian algorithm.

    This function takes a (m+1)×(n+1) matrix X of soft matching probabilities
    (including one “dummy” row and column for unmatched elements), constructs
    a cost matrix by applying –log to each entry, and solves a linear‐assignment
    problem to extract a one‐to‐one mapping.  It then returns two integer arrays:

      • map2input_edges: shape (m, 2), where each row is [map_local_idx, input_local_idx]
        or –1 if that map element is left unmatched.

      • input2map_edges: shape (n, 2), where each row is [input_local_idx, map_local_idx]
        or –1 if that input element is left unmatched.

    Args:
        X (np.ndarray): matching probability matrix of shape (m+1, n+1).  The last
                        row and column in X correspond to a “dummy” element allowing
                        for unpaired map or input items.

    Returns:
        tuple:
          map2input_edges (np.ndarray): an m×2 integer array; row i = [i, j] if map i
                                        is matched to input j, or j = –1 if unmatched.
          input2map_edges (np.ndarray): an n×2 integer array; row k = [k, i] if input k
                                        is matched to map i, or i = –1 if unmatched.
    """
    m = X.shape[0] - 1
    n = X.shape[1] - 1
    if m > 0 and n > 0:
        hungarian_cost_matrix = np.zeros((m+n, m+n))
        hungarian_cost_matrix[:m+1, :n+1] = -np.log(X + 1e-6)
        last_row = -np.log(X[-1, :] + 1e-6)
        last_col = -np.log(X[:, -1] + 1e-6)

        hungarian_cost_matrix[:m+1, n:] = np.tile(last_col.reshape(-1, 1), (1, m))
        hungarian_cost_matrix[m:, :n+1] = np.tile(last_row.reshape(1, -1), (n, 1))
        hungarian_cost_matrix[m:, n:] = -np.log(X[-1, -1] + 1e-6)

        row_idxs, col_idxs = linear_sum_assignment(hungarian_cost_matrix)

        map2input_edges = np.hstack((np.arange(m).reshape(-1, 1),
                                     -1 * np.ones((m, 1), dtype=int)))
        input2map_edges = np.hstack((np.arange(n).reshape(-1, 1),
                                     -1 * np.ones((n, 1), dtype=int)))

        for r, c in zip(row_idxs, col_idxs):
            if r < m and c < n:
                map2input_edges[r, 1] = c
                input2map_edges[c, 1] = r

    elif m == 0:
        map2input_edges = np.empty((0, 2), dtype=int)
        input2map_edges = np.hstack((np.arange(n).reshape(-1, 1),
                                     -1 * np.ones((n, 1), dtype=int)))
    else:  # n == 0
        map2input_edges = np.hstack((np.arange(m).reshape(-1, 1),
                                     -1 * np.ones((m, 1), dtype=int)))
        input2map_edges = np.empty((0, 2), dtype=int)

    return map2input_edges, input2map_edges

def get_permutation_like_matrix(
    map2input_edges: np.ndarray,
    input2map_edges: np.ndarray
) -> np.ndarray:
    """
    Build a binary “permutation‐like” matrix P from discrete edge lists.

    Given two edge‐lists:
      • map2input_edges: an array of shape (m,2) where each row is [i, j] meaning
        map element i matched to input element j (j=-1 if unmatched).
      • input2map_edges: an array of shape (n,2) where each row is [k, i] meaning
        input element k matched to map element i (i=-1 if unmatched).

    This routine constructs a (m+1)×(n+1) matrix P where:
      - P[i, j] = 1 if map i matches input j,
      - P[i, n] = 1 if map i is unmatched,
      - P[m, j] = 1 if input j is unmatched,
      - All other entries are zero.

    Args:
        map2input_edges (np.ndarray): integer array of shape (m,2),
            rows = [map_idx, input_idx] or input_idx = -1 for no match.
        input2map_edges (np.ndarray): integer array of shape (n,2),
            rows = [input_idx, map_idx] or map_idx = -1 for no match.

    Returns:
        np.ndarray: a (m+1)×(n+1) binary matrix P representing the matching.
    """
    m = map2input_edges.shape[0]
    n = input2map_edges.shape[0]
    P = np.zeros((m+1, n+1), dtype=int)

    # fill map→input matches (or mark map i unmatched at column n)
    for map_idx, inp_idx in map2input_edges:
        j = inp_idx if inp_idx != -1 else n
        P[int(map_idx), int(j)] = 1

    # fill input→map matches (or mark input j unmatched at row m)
    for inp_idx, map_idx in input2map_edges:
        i = map_idx if map_idx != -1 else m
        P[int(i), int(inp_idx)] = 1

    return P

def pad(
    matrix: np.ndarray,
    padding_const: float
) -> np.ndarray:
    # Pad matrix with one row and column with padding const
    return np.pad(matrix, ((0,1),(0,1)), constant_values=padding_const)

