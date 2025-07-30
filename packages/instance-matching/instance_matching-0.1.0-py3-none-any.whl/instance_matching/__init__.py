"""
instance_matching
-----------------
A small toolbox for extracting, matching, evaluating and visualizing
map‐level lane‐instance correspondences.
"""

# expose your CLI entry point
from .cli import main as run_cli

# evaluator
from .evaluator import run_evaluation

# extraction
from .extractor import (
    extract_gt_instances,
    extract_local_instances,
    extract_center_line_instances,
    extract_lane_divider_instances,
    sample_instances
)

# reporting
from .reporter import Reporter

# visual tools
from .visualizer import plot

# core utils
from .utils import (
    sample_linestring_with_noise,
    is_duplicate_edge,
    add_new_edge,
    sample_edge
)

from .matcher.matcher import InstanceMatcher
from .matcher.gromov_wasserstein import GromovWasserstein
from .matcher.utils import (
    one_way_chamfer_distance,
    two_way_chamfer_distance,
    build_adjacency_matrix,
    build_cross_adjacency_matrix,
    compute_gt_edges,
    to_gt_format,
    get_permutation_like_matrix,
    pad
)

__all__ = [
    # CLI
    "run_cli",
    # evaluation
    "run_evaluation",
    # extraction
    "extract_gt_instances", "extract_local_instances",
    "extract_center_line_instances", "extract_lane_divider_instances",
    "sample_instances"
    # reporting
    "Reporter",
    # visualization
    "plot",
    # low-level utilities
    "sample_linestring_with_noise", "is_duplicate_edge", "add_new_edge", "sample_edge",
    # matcher
    "InstanceMatcher", "GromovWasserstein",
    "one_way_chamfer_distance", "two_way_chamfer_distance", 
    "build_adjacency_matrix", "build_cross_adjacency_matrix",
    "compute_gt_edges", "to_gt_format", "get_permutation_like_matrix", "pad"
]
