import numpy as np
from typing import Dict, Any, Tuple, List
from shapely.geometry import LineString, MultiLineString, Polygon
import lanelet2
from lanelet2.projection import LocalCartesianProjector

from .utils import (
    interpolate_points, 
    add_new_edge, 
    sample_linestring_with_noise, 
    sample_edge, 
    get_lane_divder_instance_from_idx,
    lane_divider_connection_check
)

def extract_gt_instances(lanelet_map) -> Dict[str, Any]:
    """
    Extract ground-truth centerline and lane-divider instances from a lanelet2 map.

    Returns a dict with keys:
      - 'center_lines': {
            'pts': List[LineString],
            'edges': List[Tuple[int,int]],
            'left_lane_idxs': List[int],
            'right_lane_idxs': List[int]
        }
      - 'lane_dividers': {
            'pts': List[LineString]
        }
    """
    res = {}
    res['center_lines'] = {}
    res['center_lines']['pts'] = []
    res['center_lines']['edges'] = []
    res['center_lines']['left_lane_idxs'] = []
    res['center_lines']['right_lane_idxs'] = []

    res['lane_dividers'] = {}
    res['lane_dividers']['pts'] = []
    
    lane_divider_ids = []

    traffic_rules = lanelet2.traffic_rules.create(lanelet2.traffic_rules.Locations.Germany,
                                                    lanelet2.traffic_rules.Participants.Vehicle)
    graph = lanelet2.routing.RoutingGraph(lanelet_map, traffic_rules)
    llt_ids = np.array([llt.id for llt in lanelet_map.laneletLayer])

    for llt in lanelet_map.laneletLayer:
        if not llt.leftBound.id in lane_divider_ids:
            lane_divider_ids.append(llt.leftBound.id)
            ls = lanelet_map.lineStringLayer[llt.leftBound.id]
            res['lane_dividers']['pts'].append(LineString([(point.x, point.y) for point in ls]))
        
        if not llt.rightBound.id in lane_divider_ids:
            lane_divider_ids.append(llt.rightBound.id)
            ls = lanelet_map.lineStringLayer[llt.rightBound.id]
            res['lane_dividers']['pts'].append(LineString([(point.x, point.y) for point in ls]))

        left = np.array([[pt.x, pt.y] for pt in llt.leftBound])
        right = np.array([[pt.x, pt.y] for pt in llt.rightBound])     
        n_left = len(left)
        n_right = len(right)
        n_target = max(n_left, n_right)
        left_interp = interpolate_points(left, n_target)
        right_interp = interpolate_points(right, n_target)
        center_pts = (left_interp + right_interp)/ 2.0
        res['center_lines']['pts'].append(LineString(center_pts))

        curr_idx = np.where(llt_ids == llt.id)[0][0] + 1 # ID always start from 1.
        next_llts = graph.following(llt)
        for next_llt in next_llts:
            next_idx = np.where(llt_ids == next_llt.id)[0][0] + 1
            res['center_lines']['edges'] = add_new_edge(res['center_lines']['edges'], (curr_idx, next_idx), 'center_lines')

    for llt in lanelet_map.laneletLayer:
        left_idx = np.where(np.array(lane_divider_ids) == llt.leftBound.id)[0][0] + 1
        right_idx = np.where(np.array(lane_divider_ids) == llt.rightBound.id)[0][0] + 1
        res['center_lines']['left_lane_idxs'].append(left_idx)
        res['center_lines']['right_lane_idxs'].append(right_idx)
    
    return res

def extract_local_instances(
    lanelet_map,
    full_instances: Dict[str, Any],
    perception_box: Polygon,
    noise_std: float,
    offset_std: float
) -> Dict[str, Any]:
    """
    Clip and sample both center-line and lane-divider instances within a perception region.

    This function performs three main steps:
      1. Extract and sample center-line segments via `extract_center_line_instances`.
      2. Extract and sample lane-divider segments via `extract_lane_divider_instances`.
      3. Assemble the results into a unified structure including topology edges.

    Args:
        lanelet_map: A lanelet2 map object used for context in lane-divider extraction.
        full_instances: The full ground-truth instances dict from `extract_gt_instances`,
                        containing complete center-line geometries and precomputed edges.
        perception_box: A Shapely Polygon defining the current sensor field of view.
        noise_std:      Standard deviation of Gaussian noise to add at each sampled point.
        offset_std:     Standard deviation of a single random offset per segment,
                        simulating systematic sensor bias.

    Returns:
        A dict with the following keys:
          - 'box': Shapely Polygon, the same `perception_box` passed in.
          - 'center_lines': dict returned by `extract_center_line_instances`, containing:
                'idxs', 'pts', 'left_lane_idxs', 'right_lane_idxs', and 'edges'.
          - 'lane_dividers': dict returned by `extract_lane_divider_instances`, containing:
                'idxs', 'pts', and 'edges'.
    """
    
    # 1) Extract and sample centerline segments
    center_line_instances = extract_center_line_instances(
        full_instances,
        perception_box,
        noise_std,
        offset_std
    )

    # 2) Extract and sample lane-divider segments
    lane_divider_instances = extract_lane_divider_instances(
        lanelet_map,
        full_instances,
        center_line_instances,
        perception_box,
        noise_std,
        offset_std
    )

    # 3) Package results
    map_instances: Dict[str, Any] = {
        'box': perception_box,
        'center_lines': center_line_instances,
        'lane_dividers': lane_divider_instances
    }


    return map_instances

def extract_center_line_instances(
    full_instances: Dict[str, Any],
    perception_box: Polygon, 
    noise_std: float, 
    offset_std: float
) -> Dict[str, Any]:
    """
    Extract and sample center-line segments from the full map within a given perception region.

    For each ground-truth center-line geometry that intersects `perception_box`, this function:
      1. Clips the line to the box.
      2. Splits into one or more sub-LineStrings.
      3. Samples each sub-LineString at fixed intervals with added noise and offset.
      4. Records the corresponding GT index and its associated left/right lane-divider indices.
      5. Filters the topology edges to only those whose endpoints remain physically connected
         within the clipped region.

    Args:
        full_instances:  
            Dictionary of ground-truth instances, with keys:
              - 'center_lines': {
                    'pts': List[LineString],
                    'edges': List[Tuple[int,int]],
                    'left_lane_idxs': List[int],
                    'right_lane_idxs': List[int]
                }
        perception_box:  
            A Shapely Polygon defining the current sensor/vehicle perception area.
        noise_std:  
            Standard deviation of Gaussian noise added at each sampled point.
        offset_std:  
            Standard deviation of a random constant offset applied to each sub-LineString 
            (to simulate systematic sensor bias).

    Returns:
        A dictionary with keys:
          - 'idxs': List[int]  
            indices of the GT center_lines that were sampled (starts from 1).
          - 'pts': List[LineString]  
            The sampled, noisy sub-LineStrings within `perception_box`.
          - 'left_lane_idxs': List[int]  
            The corresponding GT left-divider index for each sampled segment.
          - 'right_lane_idxs': List[int]  
            The corresponding GT right-divider index.
          - 'edges': List[Tuple[int,int]]  
            Filtered adjacency list of sampled segments: only those whose end/start points 
            remain within `offset_std` distance are kept.
    """
    center_line_instances = {
        'idxs': [],
        'pts': [],
        'left_lane_idxs': [],
        'right_lane_idxs': []
    }
    gt_pts: List[LineString] = []

    # 1) Clip and sample each center line
    for i, center_line in enumerate(full_instances['center_lines']['pts']):
        if not perception_box.intersects(center_line):
            continue

        clipped = perception_box.intersection(center_line)
        segments = (clipped.geoms if isinstance(clipped, MultiLineString)
                    else [clipped])

        for seg in segments:
            # noisy sampling for matching, zero-noise for geometry checks
            sampled_noisy = sample_linestring_with_noise(seg, 0.2, noise_std, offset_std)
            sampled_gt    = sample_linestring_with_noise(seg, 0.2, 0.0, 0.0)

            center_line_instances['idxs'].append(i + 1)
            center_line_instances['pts'].append(sampled_noisy)
            center_line_instances['left_lane_idxs'].append(
                full_instances['center_lines']['left_lane_idxs'][i])
            center_line_instances['right_lane_idxs'].append(
                full_instances['center_lines']['right_lane_idxs'][i])
            gt_pts.append(sampled_gt)

    # 2) Filter and assign edges
    all_edges = sample_edge(
        full_instances['center_lines']['edges'],
        center_line_instances['idxs'],
        'center_lines'
    )
    valid_edges = []
    idx_array = np.array(center_line_instances['idxs'])

    for (u, v) in all_edges:
        # find sampled segments corresponding to u and v
        from_indices = np.where(idx_array == abs(u))[0]
        to_indices   = np.where(idx_array == abs(v))[0]

        # collect end/start points
        from_pts = []
        for fi in from_indices:
            pt = gt_pts[fi].coords[-1] if u > 0 else gt_pts[fi].coords[0]
            from_pts.append(np.asarray(pt))

        to_pts = []
        for ti in to_indices:
            pt = gt_pts[ti].coords[0] if v > 0 else gt_pts[ti].coords[-1]
            to_pts.append(np.asarray(pt))

        # valid if any pair is within offset_std
        connected = False
        for p_from in from_pts:
            for p_to in to_pts:
                if np.linalg.norm(p_from - p_to) <= offset_std:
                    connected = True
                    break
            if connected:
                break

        if connected:
            valid_edges.append((u, v))

    center_line_instances['edges'] = valid_edges
    return center_line_instances

def extract_lane_divider_instances(lanelet_map, full_instances, center_line_instances, perception_box, noise_std, offset_std):
    lane_divider_ids = []

    for llt in lanelet_map.laneletLayer:
        if not llt.leftBound.id in lane_divider_ids:
            lane_divider_ids.append(llt.leftBound.id)
        
        if not llt.rightBound.id in lane_divider_ids:
            lane_divider_ids.append(llt.rightBound.id)

    lane_divider_instances = {}
    lane_divider_instances['idxs'] = []
    lane_divider_instances['pts'] = []
    lane_divider_instances['edges'] = []
    gt_pts = []

    for i, div_line in enumerate(full_instances['lane_dividers']['pts']):
        if perception_box.intersects(div_line):
            inter_line_strings = perception_box.intersection(div_line)               
            lines = inter_line_strings.geoms if isinstance(inter_line_strings, MultiLineString) else [inter_line_strings]
            for line_string in lines:
                sampled_l = sample_linestring_with_noise(line_string, 0.2, noise_std, offset_std)
                gt_pts.append(sample_linestring_with_noise(line_string, 0.2, 0.0, 0.0))

                lane_divider_instances['idxs'].append(i+1)
                lane_divider_instances['pts'].append(sampled_l)
    
    # Based on the centerline connection relationship, also extract connection information of lane divider instances
    ld_idxs = lane_divider_instances['idxs']
    ld_pts = gt_pts # GT lane divider point sequences are used to correctly output the local topology reasoning results.
    for i in range(len(center_line_instances['idxs'])):
        left_lane_idx = center_line_instances['left_lane_idxs'][i]
        right_lane_idx = center_line_instances['right_lane_idxs'][i]

        left_lane_instances = get_lane_divder_instance_from_idx(ld_idxs, ld_pts, left_lane_idx)
        right_lane_instances = get_lane_divder_instance_from_idx(ld_idxs, ld_pts, right_lane_idx)

        if None in left_lane_instances:
            left_lane_idx = -1
        if None in right_lane_instances:
            right_lane_idx = -1
        
        # Search for previous or next centerlines in the centerline edges
        to_left_lane_idxs = []
        to_right_lane_idxs = []
        from_left_lane_idxs = []
        from_right_lane_idxs = []
        for from_idx, to_idx in center_line_instances['edges']: # indices in edge are global
            if from_idx == center_line_instances['idxs'][i]:
                to_idx_ = np.where(np.array(center_line_instances['idxs']) == abs(to_idx))[0][0]
                to_left_lane_idxs.append(center_line_instances['left_lane_idxs'][to_idx_])
                to_right_lane_idxs.append(center_line_instances['right_lane_idxs'][to_idx_])
            if to_idx == center_line_instances['idxs'][i]:
                from_idx_ = np.where(np.array(center_line_instances['idxs']) == abs(to_idx))[0][0]
                from_left_lane_idxs.append(center_line_instances['left_lane_idxs'][from_idx_])
                from_right_lane_idxs.append(center_line_instances['right_lane_idxs'][from_idx_])

        for left_lane_instance in left_lane_instances:
            lane_divider_instances['edges'] = addLaneDividerEdges(lane_divider_instances['edges'], ld_idxs, ld_pts, from_left_lane_idxs, "from", left_lane_instance, left_lane_idx)
            lane_divider_instances['edges'] = addLaneDividerEdges(lane_divider_instances['edges'], ld_idxs, ld_pts, to_left_lane_idxs, "to", left_lane_instance, left_lane_idx)

        for right_lane_instance in right_lane_instances:
            lane_divider_instances['edges'] = addLaneDividerEdges(lane_divider_instances['edges'], ld_idxs, ld_pts, from_right_lane_idxs, "from", right_lane_instance, right_lane_idx)
            lane_divider_instances['edges'] = addLaneDividerEdges(lane_divider_instances['edges'], ld_idxs, ld_pts, to_right_lane_idxs, "to", right_lane_instance, right_lane_idx)
    return lane_divider_instances

def addLaneDividerEdges(edges, ld_idxs, ld_pts, target_lane_idxs, from_to_flag, curr_lane_instance, curr_lane_idx):
    for target_lane_idx in target_lane_idxs:
        target_lane_instances = get_lane_divder_instance_from_idx(ld_idxs, ld_pts, target_lane_idx) 
        # There may be multiple target lane instances, since a single gt instance may be split into multiple pieces in the current perception box
        # For valid match, add the lane divider connectivity relationship to the lane divider edges
        if None in target_lane_instances:
            tmp_lane_idx = -1
        else:
            tmp_lane_idx = target_lane_idx

        if from_to_flag == "from":
            for target_lane_instance in target_lane_instances:
                valid, from_inversion_flag, to_inversion_flag = lane_divider_connection_check(target_lane_instance, curr_lane_instance, tmp_lane_idx, curr_lane_idx, ld_idxs)
                
                if valid:
                    if from_inversion_flag:
                        input_from_idx = -target_lane_idx
                    else:
                        input_from_idx = target_lane_idx

                    if to_inversion_flag:
                        input_to_idx = -curr_lane_idx
                    else:
                        input_to_idx = curr_lane_idx
                    
                    if input_from_idx != input_to_idx:
                        edges = add_new_edge(edges, (input_from_idx, input_to_idx), 'lane_dividers')

        elif from_to_flag == "to":
            for target_lane_instance in target_lane_instances:
                valid, from_inversion_flag, to_inversion_flag = lane_divider_connection_check(curr_lane_instance, target_lane_instance, curr_lane_idx, tmp_lane_idx, ld_idxs)
                
                if valid:
                    if from_inversion_flag:
                        input_from_idx = -curr_lane_idx
                    else:
                        input_from_idx = curr_lane_idx
                    
                    if to_inversion_flag:
                        input_to_idx = -target_lane_idx
                    else:
                        input_to_idx = target_lane_idx
                    
                    if input_from_idx != input_to_idx:
                        edges = add_new_edge(edges, (input_from_idx, input_to_idx), 'lane_dividers')
    
    return edges

def merge_instances(
    full_instances: Dict[str, Any],
    existing_instances: Dict[str, Any],
    input_instances: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge existing map instances with new input observations:
      - update overlapping segments
      - append/prepend new segments
      - merge edge lists
    Returns updated `existing_instances` dict.
    """
    merged_instances = {
        'box': existing_instances['box'].union(input_instances['box']),
        'center_lines': {'idxs': [], 'pts': [], 'left_lane_idxs': [], 'right_lane_idxs': [], 'edges': []},
        'lane_dividers': {'idxs': [], 'pts': [], 'edges': []}
    }

    for instance_type in ['center_lines', 'lane_dividers']:
        ex_idxs = np.array(existing_instances[instance_type]['idxs'])
        in_idxs = np.array(input_instances[instance_type]['idxs'])

        shared = np.intersect1d(ex_idxs, in_idxs)
        new = np.setdiff1d(in_idxs, ex_idxs)
        only_existing = np.setdiff1d(ex_idxs, shared)

        def append(idx, pt, source=None):
            merged_instances[instance_type]['idxs'].append(idx)
            merged_instances[instance_type]['pts'].append(sample_linestring_with_noise(pt, interval=0.2, noise_std=0, offset_std=0))
            if instance_type == 'center_lines' and source:
                merged_instances[instance_type]['left_lane_idxs'].append(source[instance_type]['left_lane_idxs'][idx-1])
                merged_instances[instance_type]['right_lane_idxs'].append(source[instance_type]['right_lane_idxs'][idx-1])

        # 1. Copy existing instances that are not in input instances
        for idx in only_existing:
            for rel_idx in np.where(ex_idxs == idx)[0]:
                merged_instances[instance_type]['idxs'].append(idx)
                merged_instances[instance_type]['pts'].append(existing_instances[instance_type]['pts'][rel_idx])
                if instance_type == 'center_lines':
                    merged_instances[instance_type]['left_lane_idxs'].append(full_instances[instance_type]['left_lane_idxs'][idx-1])
                    merged_instances[instance_type]['right_lane_idxs'].append(full_instances[instance_type]['right_lane_idxs'][idx-1])

        # 2. Update shared instances and add new instances            
        for idx in np.concatenate([shared, new]):
            geom = full_instances[instance_type]['pts'][idx-1].intersection(merged_instances['box'])
            if isinstance(geom, MultiLineString):
                for g in geom.geoms:
                    append(idx, g, full_instances)
            elif isinstance(geom, LineString):
                append(idx, geom, full_instances)

        # 3. Concatenate Edges
        merged_edges = existing_instances[instance_type]['edges']
        for edge in input_instances[instance_type]['edges']:
            merged_edges = add_new_edge(merged_edges, edge, instance_type)

        merged_instances[instance_type]['edges'] = merged_edges
    return merged_instances

def sample_instances(target_instances, perception_box):
    center_line_intersect_idxs = []
    lane_divider_intersect_idxs = []

    for i, center_line_instances in enumerate(target_instances['center_lines']['pts']):
        if perception_box.intersects(center_line_instances):
            center_line_intersect_idxs.append(i)

    for i, lane_divider_instances in enumerate(target_instances['lane_dividers']['pts']):
        if perception_box.intersects(lane_divider_instances):
            lane_divider_intersect_idxs.append(i)

    output_instances = {}
    output_instances['center_lines'] = {}
    for k, v in target_instances['center_lines'].items():
        if k != 'edges':
            sample_value = [v[i] for i in center_line_intersect_idxs]
            output_instances['center_lines'][k] = sample_value
        
    output_instances['center_lines']['edges'] = sample_edge(target_instances['center_lines']['edges'], output_instances['center_lines']['idxs'], 'center_lines')

    output_instances['lane_dividers'] = {}
    for k, v in target_instances['lane_dividers'].items():
        if  k!= 'edges':
            sample_value = [v[i] for i in lane_divider_intersect_idxs]
            output_instances['lane_dividers'][k] = sample_value

    output_instances['lane_dividers']['edges'] = sample_edge(target_instances['lane_dividers']['edges'], output_instances['lane_dividers']['idxs'], 'lane_dividers')

    return output_instances
