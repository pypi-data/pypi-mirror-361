import numpy as np
from typing import Dict, Any
from .optimization.solvers import solve_initial_geom, solve_matching_method
from .gromov_wasserstein import GromovWasserstein

from .utils import (
    one_way_chamfer_distance, 
    build_adjacency_matrix, 
    build_cross_adjacency_matrix, 
    compute_gt_edges, 
    to_gt_format,
    get_permutation_like_matrix
)

class InstanceMatcher:
    """
    Match existing map instances to new input observations using a variety of optimization-based cost functions.

    This class builds geometric, topological, and cross‐type cost matrices from two sets of lane‐level
    map elements (center‐lines and lane‐dividers), solves one or more matching problems via IPOPT
    (or Gromov–Wasserstein), and then either evaluates performance against ground truth or returns
    the raw matching for downstream map updating.

    Parameters:
        existing_instances (Dict[str, Any]):
            A dict with keys 'center_lines' and 'lane_dividers', each containing:
              - 'idxs': List[int] of 1-based GT IDs
              - 'pts': List[shapely.geometry.LineString] for each segment
              - 'edges': List[Tuple[int,int]] of connectivity in that domain
              - for center_lines: also 'left_lane_idxs' and 'right_lane_idxs'
        input_instances (Dict[str, Any]):
            Same structure as existing_instances, but for the newly observed local inference.
        config (Dict[str, Any]):
            Matching configuration with keys:
              - 'params':
                  - 'padding_cost' (float): cost for a dummy–dummy match
                  - 'weights' (List[float]): [λ_gC, λ_gL, λ_tC, λ_tL, λ_c] weights for geometry, topology, cross
                  - optional 'matrices': precomputed adjacency/cross‐adjacency matrices
              - 'mode' (str): one of "geom", "topo", "geom-topo", "fusion-base", "fusion", "ablation", "gromov-wasserstein"
              - 'eval_mode' (str): "comparison" to evaluate vs GT or "forward" to return matches
              - 'precompute' (bool): whether to load vs compute adjacency matrices

    Attributes:
        Cc (np.ndarray): (n1+1)×(n2+1) cost matrix of one‐way Chamfer distances for center‐lines.
        Cl (np.ndarray): (n3+1)×(n4+1) cost matrix for lane‐dividers.
        Ac1, Ac2, Al1, Al2 (np.ndarray): adjacency matrices for existing/input center‐lines and dividers.
        Acl1_left, Acl1_right, Acl2_left, Acl2_right (np.ndarray):
            cross‐adjacency matrices linking center‐lines to their left/right dividers.
        gt (Dict[str, Dict[str, np.ndarray]]):
            Ground‐truth map2input and input2map edges for evaluation.
        results (Dict[str, Dict[str, np.ndarray]]):
            Will hold the computed map2input and input2map edges after matching.

    Public Methods:
        match() -> Dict[str, Any]:
            Execute the matching pipeline according to `config['mode']` and `config['eval_mode']`.
            Returns either an evaluation report or the raw match edges.
        evaluate(Xs, Ys) -> Dict[str, Any]:
            Given one or more matching matrices Xs, Ys, compute TP/FP/FN and topological consistency.
        forward(Xs, Ys) -> Dict[str, Any]:
            Convert a single matching solution into explicit map2input / input2map edge lists.

    Internal Helpers:
        fillGeomMatchingCost(), fillAdjacencyMatrix(), fillCrossAdjacencyMatrix(), createGT(), ...
        toGTFormat(), etc.

    Example:
        >>> matcher = InstanceMatcher(existing_instances, input_instances, config)
        >>> report = matcher.match()

    Implemented by Jinhwan Jeon, 2025
    """
    def __init__(self, existing_instances, input_instances, config):
        self.existing_instances = existing_instances
        self.input_instances = input_instances
        self.config = config

        n1 = len(self.existing_instances['center_lines']['pts'])
        n2 = len(self.input_instances['center_lines']['pts'])
        n3 = len(self.existing_instances['lane_dividers']['pts'])
        n4 = len(self.input_instances['lane_dividers']['pts'])
        self.Cc = self.config['params']['padding_cost'] * np.ones((n1+1, n2+1))
        self.Cl = self.config['params']['padding_cost'] * np.ones((n3+1, n4+1))

        self.gt = {}
        self.gt['center_lines'] = {}
        self.gt['lane_dividers'] = {}
        self.gt['center_lines']['map2input_edges'] = np.hstack((np.arange(n1).reshape(-1, 1), (-1)*np.ones((n1,1))))
        self.gt['center_lines']['input2map_edges'] = np.hstack((np.arange(n2).reshape(-1, 1), (-1)*np.ones((n2,1))))
        self.gt['lane_dividers']['map2input_edges'] = np.hstack((np.arange(n3).reshape(-1, 1), (-1)*np.ones((n3,1))))
        self.gt['lane_dividers']['input2map_edges'] = np.hstack((np.arange(n4).reshape(-1, 1), (-1)*np.ones((n4,1))))

        self.results = {}
        self.results['center_lines'] = {}
        self.results['lane_dividers'] = {}
        self.results['center_lines']['map2input_edges'] = None
        self.results['center_lines']['input2map_edges'] = None
        self.results['lane_dividers']['map2input_edges'] = None
        self.results['lane_dividers']['input2map_edges'] = None

        # Initialize fixed matrices
        # These matrices are assumed to be known before optimization, and also accurate
        self.fillGeomMatchingCost()

        if not self.config['precompute']:
            self.fillAdjacencyMatrix()
            self.fillCrossAdjacencyMatrix()
        else:
            try:
                self.Ac1 = self.config['params']['matrices']['Ac1']
                self.Al1 = self.config['params']['matrices']['Al1']
                self.Ac2 = self.config['params']['matrices']['Ac2']
                self.Al2 = self.config['params']['matrices']['Al2']
                self.Acl1_left = self.config['params']['matrices']['Acl1_left']
                self.Acl1_right = self.config['params']['matrices']['Acl1_right']
                self.Acl2_left = self.config['params']['matrices']['Acl2_left']
                self.Acl2_right = self.config['params']['matrices']['Acl2_right']
            except KeyError:
                raise ValueError("Pre-computed matrices are not provided in the config. Set 'precompute' to True to compute them on-the-fly.")

        # if self.config['eval_mode'] == "comparison":
            # Create ground truth matching result for future evaluation
        self.createGT()

    def fillGeomMatchingCost(self):
        # Centerline
        for i, existing_center_line in enumerate(self.existing_instances['center_lines']['pts']):
            for j, input_center_line in enumerate(self.input_instances['center_lines']['pts']):                
                self.Cc[i,j] = one_way_chamfer_distance(existing_center_line, input_center_line)

        # Lane Divider
        for i, existing_lane_divider in enumerate(self.existing_instances['lane_dividers']['pts']):
            for j, input_lane_divider in enumerate(self.input_instances['lane_dividers']['pts']):                
                self.Cl[i,j] = one_way_chamfer_distance(existing_lane_divider, input_lane_divider)
    
    def fillAdjacencyMatrix(self):
        n1 = len(self.existing_instances['center_lines']['pts']) + 1
        n2 = len(self.input_instances  ['center_lines']['pts']) + 1
        self.Ac1 = build_adjacency_matrix(self.existing_instances['center_lines']['edges'], n1)
        self.Ac2 = build_adjacency_matrix(self.input_instances  ['center_lines']['edges'], n2)

        n3 = len(self.existing_instances['lane_dividers']['pts']) + 1
        n4 = len(self.input_instances  ['lane_dividers']['pts']) + 1
        self.Al1 = build_adjacency_matrix(self.existing_instances['lane_dividers']['edges'], n3, symmetric=True)
        self.Al2 = build_adjacency_matrix(self.input_instances  ['lane_dividers']['edges'], n4, symmetric=True)

    def fillCrossAdjacencyMatrix(self):
        self.Acl1_left, self.Acl1_right = build_cross_adjacency_matrix(
            self.existing_instances['center_lines'], self.existing_instances['lane_dividers']
        )
        self.Acl2_left, self.Acl2_right = build_cross_adjacency_matrix(
            self.input_instances  ['center_lines'], self.input_instances  ['lane_dividers']
        )

    def createGT(self):
        mc, ic = np.array(self.existing_instances['center_lines']['idxs']), np.array(self.input_instances['center_lines']['idxs'])
        self.gt['center_lines']['map2input_edges'], self.gt['center_lines']['input2map_edges'] = compute_gt_edges(mc, ic)

        ml, il = np.array(self.existing_instances['lane_dividers']['idxs']), np.array(self.input_instances['lane_dividers']['idxs'])
        self.gt['lane_dividers']['map2input_edges'], self.gt['lane_dividers']['input2map_edges'] = compute_gt_edges(ml, il)

    def match(self) -> Dict[str, Any]:
        # --- 1) select which methods to run ---
        if self.config["mode"] == "ablation":
            methods      = ["geom","topo","geom-topo","fusion-base","fusion","gromov-wasserstein"]
            reduced_flag = {"geom":False, "topo":True, "geom-topo":True, "fusion-base":False, "fusion":True}
        elif self.config["mode"] == "fusion-base":
            methods      = ["fusion-base"]
            reduced_flag = {"fusion-base":False}
        else:
            m            = self.config["mode"]
            methods      = [m]
            reduced_flag = {m: True}

        # --- 2) geometry‐only init ---
        X_init, Y_init = solve_initial_geom(
            self.Cc, self.Cl,
            self.Ac1, self.Ac2, self.Al1, self.Al2,
            self.Acl1_left, self.Acl1_right, self.Acl2_left, self.Acl2_right,
            padding_cost=self.config["params"]["padding_cost"],
            weights=self.config["params"]["weights"],
            precompute=self.config["precompute"],
            matrices=self.config["params"].get("matrices")
        )

        opt_X, opt_Y = {}, {}

        # --- 3) run each method ---
        for method in methods:
            if method == "geom":
                opt_X[method], opt_Y[method] = X_init, Y_init

            elif method == "gromov-wasserstein":
                gw = GromovWasserstein(
                    self.existing_instances,
                    self.input_instances,
                    self.config["params"]["padding_cost"]
                )
                opt_X[method], opt_Y[method] = gw.match()

            else:
                X, Y = solve_matching_method(
                    method,
                    X_init, Y_init,
                    self.Cc, self.Cl,
                    self.Ac1, self.Ac2, self.Al1, self.Al2,
                    self.Acl1_left, self.Acl1_right, self.Acl2_left, self.Acl2_right,
                    padding_cost=self.config["params"]["padding_cost"],
                    weights=self.config["params"]["weights"],
                    use_reduced=reduced_flag[method]
                )
                opt_X[method], opt_Y[method] = X, Y

        # --- 4) return evaluation or forward results ---
        if self.config["eval_mode"] == "comparison":
            return self.evaluate(opt_X, opt_Y)
        else:
            return self.forward(opt_X, opt_Y)
    
    def evaluate(self, Xs, Ys) -> Dict[str,Any]:
        """
        Evaluate optimization results of (possibly) multiple types of matching costs        
        
        """
        report = {}

        for method in Xs.keys(): 
            report[method] = {}

            # Centerline matching
            X = Xs[method]
            map2input_edges_c, input2map_edges_c = to_gt_format(X)
            P_X = get_permutation_like_matrix(map2input_edges_c, input2map_edges_c)
            report[method]['center_lines'] = self.compareMatch(map2input_edges_c, input2map_edges_c, P_X, self.gt['center_lines'], 'center_lines')

            # Lane divider matching
            Y = Ys[method]
            map2input_edges_l, input2map_edges_l = to_gt_format(Y)
            P_Y = get_permutation_like_matrix(map2input_edges_l, input2map_edges_l)
            report[method]['lane_dividers'] = self.compareMatch(map2input_edges_l, input2map_edges_l, P_Y, self.gt['lane_dividers'], 'lane_dividers')

            # Cross-type TCS
            report[method]['cross_TCS'] = self.computeCrossTCS(P_X, P_Y)
        return report
    
    def forward(self, Xs, Ys) -> Dict[str,Any]:
        """
        Obtain optimization results of (possibly) multiple types of matching costs

        """
        report = {}
        
        for method, X in Xs.items():
            report[method] = {}
            map2input_edges_c, input2map_edges_c = to_gt_format(X)
            report[method]['center_lines'] = {}
            report[method]['center_lines']['map2input_edges'] = map2input_edges_c
            report[method]['center_lines']['input2map_edges'] = input2map_edges_c

        for method, Y in Ys.items():
            map2input_edges_l, input2map_edges_l = to_gt_format(Y)
            report[method]['lane_dividers'] = {}
            report[method]['lane_dividers']['map2input_edges'] = map2input_edges_l
            report[method]['lane_dividers']['input2map_edges'] = input2map_edges_l
        
        return report

    def compareMatch(
        self,
        map2input_edges: np.ndarray,
        input2map_edges: np.ndarray,
        P: np.ndarray,
        gt: Dict[str, np.ndarray],
        instance_type: str
    ) -> Dict[str, float]:
        """
        Compute precision/recall/F1 counts and Topological Consistency Score for one instance type.

        This routine first gathers the predicted and ground-truth edge sets (treating map→input
        and input→map edges symmetrically), then computes true positives (TP), false positives (FP),
        and false negatives (FN).  It also projects the adjacency matrices through the permutation
        matrix P to measure how well connectivity is preserved in both directions.

        Args:
            map2input_edges (np.ndarray):
                Predicted map→input edge list of shape (m,2), rows = (map_idx, input_idx).
            input2map_edges (np.ndarray):
                Predicted input→map edge list of shape (n,2), rows = (input_idx, map_idx).
            P (np.ndarray):
                The (m+1)×(n+1) binary matching matrix from getPermutationLikeMatrix.
            gt (Dict[str, np.ndarray]):
                Ground-truth dict containing 'map2input_edges' and 'input2map_edges' arrays.
            instance_type (str):
                One of 'center_lines' or 'lane_dividers', selects which adjacency matrices to use.

        Returns:
            Dict[str, float]: A dictionary with keys:
                - 'TP': number of correctly predicted edges
                - 'FP': number of false positive edges
                - 'FN': number of false negative edges
                - 'Total': total number of GT edges
                - 'n12': count of preserved adjacency when projecting map→input→map
                - 'd12': total possible adjacency in the input graph
                - 'n21': count of preserved adjacency when projecting input→map→input
                - 'd21': total possible adjacency in the map graph
        """
        map2input_edges_gt = gt['map2input_edges']
        input2map_edges_gt = gt['input2map_edges']

        def collect_edges(edge_list_1, edge_list_2):
            edge_set = set()
            for src, tgt in edge_list_1:
                edge_set.add((src, tgt))
            for src, tgt in edge_list_2:
                if (tgt, src) not in edge_set:
                    edge_set.add((tgt, src))
            return edge_set
        # TP, FP, FN
        pred_edges = collect_edges(map2input_edges, input2map_edges)
        gt_edges = collect_edges(map2input_edges_gt, input2map_edges_gt)

        true_positive = len(pred_edges & gt_edges)
        false_positive = len(pred_edges - gt_edges)
        false_negative = len(gt_edges - pred_edges)

        # Topological Consistency Score
        if instance_type == 'center_lines':
            A1 = self.Ac1
            A2 = self.Ac2
            A1_proj = P.T @ self.Ac1 @ P
            A2_proj = P @ self.Ac2 @ P.T
        elif instance_type == 'lane_dividers':
            A1 = self.Al1
            A2 = self.Al2
            A1_proj = P.T @ self.Al1 @ P
            A2_proj = P @ self.Al2 @ P.T

        n12 = np.sum(np.multiply(A1_proj[:-1,:-1], A2[:-1,:-1]))
        d12 = np.sum(A2[:-1,:-1])

        n21 = np.sum(np.multiply(A2_proj[:-1,:-1], A1[:-1,:-1]))
        d21 = np.sum(A1[:-1,:-1])

        return {
            'TP': true_positive,
            'FP': false_positive,
            'FN': false_negative,
            'Total': len(gt_edges),
            'n12': n12,
            'd12': d12,
            'n21': n21,
            'd21': d21
        }

    def computeCrossTCS(self, P_X: np.ndarray, P_Y: np.ndarray) -> Dict[str, int]:
        """
        Compute the Cross‐Type Topological Consistency Score (TCS) between center‐lines and lane‐dividers.

        This method projects the ground‐truth cross‐adjacency matrices through the two matchings
        P_X (center→divider) and P_Y (divider→center), and then counts how many cross‐type connections
        are preserved in each direction.

        Steps:
        1. Project existing center→left and center→right adjacency via P_Xᵀ·Acl1·P_Y.
        2. Project input   center→left and center→right adjacency via P_X·Acl2·P_Yᵀ.
        3. For each of the left/right channels, compute:
            • n12 = # edges preserved when projecting map→input adjacency into the input graph
            • d12 = total edges in the input graph
            • n21 = # edges preserved when projecting input→map adjacency into the map graph
            • d21 = total edges in the map graph
        4. Sum left and right contributions to produce overall cross‐type counts.

        Note that last rows and columns are not used for computation, to prevent contamination from dummy nodes

        Args:
            P_X (np.ndarray): (m+1)×(p+1) matching matrix for center_lines ↔ input center_lines.
            P_Y (np.ndarray): (n+1)×(q+1) matching matrix for lane_dividers ↔ input lane_dividers.

        Returns:
            Dict[str, int]:
                {
                'n12': total preserved center→divider edges in the input graph,
                'd12': total possible center→divider edges in the input graph,
                'n21': total preserved divider→center edges in the map graph,
                'd21': total possible divider→center edges in the map graph
                }
        """
        Acl1_left_proj  = P_X.T @ self.Acl1_left @ P_Y
        Acl1_right_proj = P_X.T @ self.Acl1_right @ P_Y
        Acl2_left_proj  = P_X @ self.Acl2_left @ P_Y.T
        Acl2_right_proj = P_X @ self.Acl2_right @ P_Y.T

        n12_left = np.sum(Acl1_left_proj[:-1, :-1] * self.Acl2_left[:-1, :-1])
        d12_left = np.sum(self.Acl2_left[:-1, :-1])

        n12_right = np.sum(Acl1_right_proj[:-1, :-1] * self.Acl2_right[:-1, :-1])
        d12_right = np.sum(self.Acl2_right[:-1, :-1])

        n21_left = np.sum(Acl2_left_proj[:-1, :-1] * self.Acl1_left[:-1, :-1])
        d21_left = np.sum(self.Acl1_left[:-1, :-1])

        n21_right = np.sum(Acl2_right_proj[:-1, :-1] * self.Acl1_right[:-1, :-1])
        d21_right = np.sum(self.Acl1_right[:-1, :-1])

        return {
            'n12': n12_left + n12_right,
            'd12': d12_left + d12_right,
            'n21': n21_left + n21_right,
            'd21': d21_left + d21_right
        }

    def getGT(self):
        return self.gt
    
