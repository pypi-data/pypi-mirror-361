import numpy as np
import ot
from scipy.spatial.distance import cdist
from shapely.geometry import LineString
from typing import List

from .utils import two_way_chamfer_distance, pad

class GromovWasserstein:
    """
    Two-way Chamfer + OT graph matching as an ablation.

    Implemented by Jinhwan Jeon, 2025
    """
    def __init__(self, existing_instances, input_instances, padding_const):
        self.existing_instances = existing_instances
        self.input_instances = input_instances
        self.Dc1 = pad(self.fill_distance_matrix(self.existing_instances['center_lines']['pts']), padding_const)
        self.Dc2 = pad(self.fill_distance_matrix(self.input_instances['center_lines']['pts']), padding_const)
        self.Dl1 = pad(self.fill_distance_matrix(self.existing_instances['lane_dividers']['pts']), padding_const)
        self.Dl2 = pad(self.fill_distance_matrix(self.input_instances['lane_dividers']['pts']), padding_const)

        self.Dc1[-1, -1] = 0.0
        self.Dc2[-1, -1] = 0.0
        self.Dl1[-1, -1] = 0.0
        self.Dl2[-1, -1] = 0.0

    def match(self):
        epsilon = 0.03

        # Centerlines
        nc = len(self.existing_instances['center_lines']['pts'])
        mc = len(self.input_instances['center_lines']['pts'])

        if nc == 0:
            pc = np.array([1.0])
        else:
            pc = np.concatenate([np.ones(nc) * (1-epsilon) / nc, [epsilon]])
        
        if mc == 0:
            qc = np.array([1.0])
        else:
            qc = np.concatenate([np.ones(mc) * (1-epsilon) / mc, [epsilon]])

        gw_c = ot.gromov_wasserstein(self.Dc1, self.Dc2, pc, qc, loss_fun='square_loss', verbose=False)

        # Lane Dividers
        nl = len(self.existing_instances['lane_dividers']['pts'])
        ml = len(self.input_instances['lane_dividers']['pts'])
        if nl == 0:
            pl = np.array([1.0])
        else:
            pl = np.concatenate([np.ones(nl) * (1-epsilon) / nl, [epsilon]])
        
        if ml == 0:
            ql = np.array([1.0])
        else:
            ql = np.concatenate([np.ones(ml) * (1-epsilon) / ml, [epsilon]])

        gw_l = ot.gromov_wasserstein(self.Dl1, self.Dl2, pl, ql, loss_fun='square_loss', verbose=False)

        return gw_c, gw_l
    
    @staticmethod
    def fill_distance_matrix(instances: List[LineString]) -> np.ndarray:
        n = len(instances)
        D = np.zeros((n, n))
        for i, instance1 in enumerate(instances):
            for j, instance2 in enumerate(instances):
                D[i, j] = two_way_chamfer_distance(instance1, instance2)
        return D
