import os
import pickle
from typing import Dict, Any, Union

from shapely.geometry import Polygon, MultiPolygon
from lanelet2.projection import LocalCartesianProjector
from lanelet2.io import load, Origin

from .extractor import (
    extract_gt_instances,
    extract_local_instances,
    merge_instances,
    sample_instances
)
from .matcher.matcher import InstanceMatcher
from .reporter import Reporter
from .utils import convert_global_to_local
from .visualizer import plot


def run_evaluation(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run instance-instance matching evaluation (and optional incremental update) per map.

    Configuration parameters (via `config` dict):
      mode (str): Test mode selection:
        - "matching": perform map-instance matching only
        - "update-base": matching + incremental map extension without DELETE or complex changes
        - "update": full dynamic update (additions, deletions, extensions)

      map_names (List[str]): List of map identifiers to evaluate.
      data_root (str): Base directory containing OSM and pickle trip data for each map.
      map_origins (Dict[str, Tuple[float,float]]): Latitude/longitude origins per map.

    matching sub-config (config['match']):
      mode (str): Matching cost function selection:
        "ablation", "geom", "topo", "geom-topo", \
        "fusion-base", "fusion", "gromov-wasserstein"
      eval_mode (str): Evaluation style:
        "comparison" (compare to GT) or "forward" (return matches for update)
      params (Dict): Model parameters:
        - padding_cost (float): cost for unmatched padding (e.g. lane width)
        - weights (List[float]): [lambda_gC, lambda_gL, lambda_tC, lambda_tL, lambda_c]
      verbose (str): Visualization level: "none", "final", "iter-detailed"
      precompute (bool): Use precomputed cost/adjacency if True.

    noise_std (float): Gaussian noise std for point sampling.
    offset_std (float): Offset noise std for line sampling.

    Returns:
        A dict of final reports, keyed by map name.  Each report contains:
          - AP: average precision per instance type and mAP
          - edge: precision/recall/F1 for intra-type edges
          - cross_edge: precision/recall/F1 for cross-type edges

    Implemented by Jinhwan Jeon, 2025
    """
    reporter = Reporter(config['mode'])

    for map_name in config['map_names']:
        # 1) Load lanelet map and set up projector
        lat, lon = config['map_origins'][map_name]
        projector = LocalCartesianProjector(Origin(lat, lon))
        lanelet_map = load(os.path.join(config['data_root'], f"{map_name}.osm"), projector)

        # 2) Load ground truth trip data
        with open(os.path.join(config['data_root'], f"{map_name}.pkl"), 'rb') as f:
            trip_data = pickle.load(f)

        # 3) Extract full GT instances from the map
        full_instances = extract_gt_instances(lanelet_map)

        # Initialize perception box to None (no prior map)
        perception_box = None

        # 4) Loop over trips and frames
        for trip_idx, frames in enumerate(trip_data.values(), start=1):
            for frame_idx, frame in enumerate(frames, start=1):
                input_box = Polygon(frame['box'])

                if perception_box is None:
                    # First frame: initialize existing instances
                    existing_instances = extract_local_instances(
                        lanelet_map, full_instances, input_box, config['match']['noise_std'], config['match']['offset_std']
                    )
                    perception_box = input_box
                    continue

                # 5) Extract new observations
                input_instances = extract_local_instances(
                    lanelet_map, full_instances, input_box, config['match']['noise_std'], config['match']['offset_std']
                )

                # 6) Perform matching and collect reports

                reports = match_mini(existing_instances, input_instances, perception_box, input_box, config)
                reporter.update(map_name, reports)

                # 7) Update existing map instances (GT)
                existing_instances = merge_instances(full_instances, existing_instances, input_instances)

                # 8) Expand perception box
                perception_box = perception_box.union(input_box)

                # 9) Print live progress
                reporter.print(map_name, trip_idx, len(trip_data), frame_idx, len(frames))

        # 10) Save final report for this map
        reporter.save(map_name)

    return reporter.report

def match_mini(
    existing_instances: Dict[str, Any], 
    input_instances: Dict[str, Any], 
    map_perception_box: Union[MultiPolygon, Polygon], 
    input_box: Polygon, 
    config: Dict[str, Any]
) -> Dict[str, Any]:
    intersection = map_perception_box.intersection(input_box)
    reports = []

    def process_one_polygon(poly, plot_flag=False):
        if poly.is_empty:
            return

        sample_existing = sample_instances(existing_instances, poly)
        sample_input = sample_instances(input_instances, poly)

        def is_empty(sample):
            return (len(sample['center_lines']['pts']) == 0 and
                    len(sample['lane_dividers']['pts']) == 0)

        if is_empty(sample_existing) and is_empty(sample_input):
            return
        
        ex_c_idxs = sample_existing['center_lines']['idxs']
        ex_c_pts = sample_existing['center_lines']['pts']
        ex_l_idxs = sample_existing['lane_dividers']['idxs']
        ex_l_pts = sample_existing['lane_dividers']['pts']
        in_c_idxs = sample_input['center_lines']['idxs']
        in_c_pts = sample_input['center_lines']['pts']
        in_l_idxs = sample_input['lane_dividers']['idxs']
        in_l_pts = sample_input['lane_dividers']['pts']

        sample_existing['center_lines']['edges'] = convert_global_to_local(sample_existing['center_lines']['edges'], ex_c_idxs, ex_c_pts)
        sample_existing['lane_dividers']['edges'] = convert_global_to_local(sample_existing['lane_dividers']['edges'], ex_l_idxs, ex_l_pts)
        sample_input['center_lines']['edges'] = convert_global_to_local(sample_input['center_lines']['edges'], in_c_idxs, in_c_pts)
        sample_input['lane_dividers']['edges'] = convert_global_to_local(sample_input['lane_dividers']['edges'], in_l_idxs, in_l_pts)

        # For users who want to test or attach custom instance matching algorithms, 
        # modify this part of the code. 
        matcher = InstanceMatcher(sample_existing, sample_input, config['match'])
        reports.append(matcher.match())

        # if plot_flag:
        #     plot(sample_existing, sample_input, map_perception_box, input_box)

    if isinstance(intersection, Polygon):            
            process_one_polygon(intersection)

    elif isinstance(intersection, MultiPolygon):
        for poly in intersection.geoms:
            process_one_polygon(poly, True)

    return reports
