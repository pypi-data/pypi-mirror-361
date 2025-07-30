import numpy as np
from scipy.sparse import csr_matrix, coo_matrix, issparse
from .utils import trace, convert_adjacency_matrix

class OptimizationProblem:
    """
    OptimizationProblem module provides the cost function, gradient and constraint for optimization.

    Implemented by Jinhwan Jeon, 2025
    """
    def __init__(self, n, m, mode, reduce_bool, sparse_params, matrix_params, config):
        self.n = n
        self.m = m
        # Matching mode
        self.mode = mode
        # Parameter reduction boolean
        self.reduce_bool = reduce_bool

        self.I = {}
        self.J = {}
        self.I['x'] = sparse_params['Ix']
        self.I['y'] = sparse_params['Iy']
        self.J['x'] = sparse_params['Jx']
        self.J['y'] = sparse_params['Jy']
        
        self.VarIdx = {}
        self.VarIdx['x'] = np.arange(len(self.I['x']))
        self.VarIdx['y'] = np.arange(len(self.VarIdx['x']), len(self.VarIdx['x']) + len(self.I['y']))

        self.config = config
        self.Cc = matrix_params['Cc']
        self.Cl = matrix_params['Cl']
        self.Ac1 = convert_adjacency_matrix(matrix_params['Ac1'])
        self.Ac2 = convert_adjacency_matrix(matrix_params['Ac2'])
        self.Al1 = convert_adjacency_matrix(matrix_params['Al1'])
        self.Al2 = convert_adjacency_matrix(matrix_params['Al2'])
        self.Acl1_left = convert_adjacency_matrix(matrix_params['Acl1_left'])
        self.Acl1_right = convert_adjacency_matrix(matrix_params['Acl1_right'])
        self.Acl2_left = convert_adjacency_matrix(matrix_params['Acl2_left'])
        self.Acl2_right = convert_adjacency_matrix(matrix_params['Acl2_right'])
        
        self.lambda_gC, self.lambda_gL, self.lambda_tC, self.lambda_tL, self.lambda_c = self.config['params']['weights']

        n1 = self.Ac1.shape[0] - 1
        n2 = self.Ac2.shape[0] - 1
        n3 = self.Al1.shape[0] - 1
        n4 = self.Al2.shape[0] - 1

        # Initialize linear constraints
        if self.reduce_bool:
            total_var = len(self.I['x']) + len(self.I['y'])
            total_constraint = n1 + n2 + n3 + n4
            self.Aeq = np.zeros((total_constraint, total_var))
            self.beq = np.ones(total_constraint)

            for i in range(n1):
                rel_idxs = np.where(self.I['x'] == i)[0]
                self.Aeq[i, self.VarIdx['x'][rel_idxs]] = 1
            
            for i in range(n2):
                rel_idxs = np.where(self.J['x'] == i)[0]
                self.Aeq[n1 + i, self.VarIdx['x'][rel_idxs]] = 1

            for i in range(n3):
                rel_idxs = np.where(self.I['y'] == i)[0]
                self.Aeq[n1 + n2 + i, self.VarIdx['y'][rel_idxs]] = 1

            for i in range(n4):
                rel_idxs = np.where(self.J['y'] == i)[0]
                self.Aeq[n1 + n2 + n3 + i, self.VarIdx['y'][rel_idxs]] = 1
        else:
            num_x = (n1 + 1) * (n2 + 1)
            num_y = (n3 + 1) * (n4 + 1)
            total_var = num_x + num_y
            total_constraint = n1 + n2 + n3 + n4

            x0_idxs = np.arange(num_x).reshape(n1+1, n2+1)
            y0_idxs = np.arange(num_x, num_x + num_y).reshape(n3+1, n4+1)

            self.Aeq = np.zeros((total_constraint, total_var))
            self.beq = np.ones(total_constraint)

            for i in range(n1):
                self.Aeq[i, x0_idxs[i, :]] = 1
            for i in range(n2):
                self.Aeq[n1 + i, x0_idxs[:, i]] = 1
            for i in range(n3):
                self.Aeq[n1 + n2 + i, y0_idxs[i, :]] = 1
            for i in range(n4):
                self.Aeq[n1 + n2 + n3 + i, y0_idxs[:, i]] = 1
        
        self.Aeq = csr_matrix(self.Aeq)
    
    def objective(self, x): 
        n1 = self.Ac1.shape[0] - 1
        n2 = self.Ac2.shape[0] - 1
        n3 = self.Al1.shape[0] - 1
        n4 = self.Al2.shape[0] - 1

        cut_length = len(self.I['x']) if self.reduce_bool else (n1+1) * (n2+1)
        Vx = x[:cut_length]
        Vy = x[cut_length:]
        X = coo_matrix((Vx, (self.I['x'], self.J['x'])), shape=(n1+1, n2+1)).toarray() if self.reduce_bool else Vx.reshape(n1+1, n2+1)
        Y = coo_matrix((Vy, (self.I['y'], self.J['y'])), shape=(n3+1, n4+1)).toarray() if self.reduce_bool else Vy.reshape(n3+1, n4+1)

        # Geometry cost
        geom_cost = (
            self.lambda_gC * trace(self.Cc.T @ X) +
            self.lambda_gL * trace(self.Cl.T @ Y)
        )

        # Topology cost (Deprecated)

        # topo_cost = -(
        #     self.lambda_tC * (self.trace(self.Ac1.T @ X @ self.Ac2 @ X.T)) + 
        #     self.lambda_tL * (self.trace(self.Al1.T @ Y @ self.Al2 @ Y.T))
        # )

        # Topology cost
        S_c1 = np.eye(n1, n1+1)
        S_c2 = np.eye(n2, n2+1)
        S_l1 = np.eye(n3, n3+1)
        S_l2 = np.eye(n4, n4+1)

        Ac1_no_pad = S_c1 @ self.Ac1 @ S_c1.T
        Al1_no_pad = S_l1 @ self.Al1 @ S_l1.T
        Ac2_no_pad = S_c2 @ self.Ac2 @ S_c2.T
        Al2_no_pad = S_l2 @ self.Al2 @ S_l2.T
        Ac2_proj_trim = S_c1 @ X @ self.Ac2 @ X.T @ S_c1.T
        Al2_proj_trim = S_l1 @ Y @ self.Al2 @ Y.T @ S_l1.T
        Ac1_proj_trim = S_c2 @  X.T @ self.Ac1 @ X @ S_c2.T
        Al1_proj_trim = S_l2 @ Y.T @ self.Al1 @ Y @ S_l2.T
        
        topo_cost = -(
            self.lambda_tC * (trace(Ac1_no_pad.T @ Ac2_proj_trim) + trace(Ac2_no_pad.T @ Ac1_proj_trim)) + 
            self.lambda_tL * (trace(Al1_no_pad.T @ Al2_proj_trim) + trace(Al2_no_pad.T @ Al1_proj_trim))
        )

        # Cross cost (Deprecated)
        # cross_cost = -(
        #     self.lambda_c * self.trace(self.Acl1.T @ X @ self.Acl2 @ Y.T)
        # )

        # Cross cost 
        Acl1_left_no_pad = S_c1 @ self.Acl1_left @ S_l1.T
        Acl1_right_no_pad = S_c1 @ self.Acl1_right @ S_l1.T
        Acl2_left_no_pad = S_c2 @ self.Acl2_left @ S_l2.T
        Acl2_right_no_pad = S_c2 @ self.Acl2_right @ S_l2.T
        Acl2_left_proj_trim = S_c1 @ X @ self.Acl2_left @ Y.T @ S_l1.T
        Acl2_right_proj_trim = S_c1 @ X @ self.Acl2_right @ Y.T @ S_l1.T
        Acl1_left_proj_trim = S_c2 @ X.T @ self.Acl1_left @ Y @ S_l2.T
        Acl1_right_proj_trim = S_c2 @ X.T @ self.Acl1_right @ Y @ S_l2.T
        cross_cost = -(
            self.lambda_c * (trace(Acl1_left_no_pad.T @ Acl2_left_proj_trim) + trace(Acl2_left_no_pad.T @ Acl1_left_proj_trim) + 
                             trace(Acl1_right_no_pad.T @ Acl2_right_proj_trim) + trace(Acl2_right_no_pad.T @ Acl1_right_proj_trim)) 
        )

        mode_costs = {
            "geom": geom_cost,
            "topo": topo_cost,
            "geom-topo": geom_cost + topo_cost,
            "fusion-base": geom_cost + topo_cost + cross_cost,
            "fusion": geom_cost + topo_cost + cross_cost
        }
        # print(geom_cost, topo_cost, cross_cost)
        f = mode_costs[self.mode]
        return f
    
    def gradient(self, x):
        n1 = self.Ac1.shape[0] - 1
        n2 = self.Ac2.shape[0] - 1
        n3 = self.Al1.shape[0] - 1
        n4 = self.Al2.shape[0] - 1

        cut_length = len(self.I['x']) if self.reduce_bool else (n1+1) * (n2+1)
        Vx = x[:cut_length]
        Vy = x[cut_length:]
        X = coo_matrix((Vx, (self.I['x'], self.J['x'])), shape=(n1+1, n2+1)).toarray() if self.reduce_bool else Vx.reshape(n1+1, n2+1)
        Y = coo_matrix((Vy, (self.I['y'], self.J['y'])), shape=(n3+1, n4+1)).toarray() if self.reduce_bool else Vy.reshape(n3+1, n4+1)

        gradX_geom = self.lambda_gC * self.Cc
        gradY_geom = self.lambda_gL * self.Cl

        S_c1 = np.eye(n1, n1+1)
        S_c1_tilde = S_c1.T @ S_c1
        S_c2 = np.eye(n2, n2+1)
        S_c2_tilde = S_c2.T @ S_c2
        S_l1 = np.eye(n3, n3+1)
        S_l1_tilde = S_l1.T @ S_l1
        S_l2 = np.eye(n4, n4+1)
        S_l2_tilde = S_l2.T @ S_l2
        
        Ac1_no_pad = self.Ac1[:-1,:-1]
        Al1_no_pad = self.Al1[:-1,:-1]
        Ac2_no_pad = self.Ac2[:-1,:-1]
        Al2_no_pad = self.Al2[:-1,:-1]

        # gradX_topo = -self.lambda_tC * (self.Ac1.T @ X @ self.Ac2 + self.Ac1 @ X @ self.Ac2.T)
        # gradY_topo = -self.lambda_tL * (self.Al1.T @ Y @ self.Al2 + self.Al1 @ Y @ self.Al2.T)
        
        gradX_topo = -self.lambda_tC * (
            S_c1_tilde @ self.Ac1 @ S_c1_tilde @ X @ self.Ac2.T + 
            S_c1_tilde @ self.Ac1.T @ S_c1_tilde @ X @ self.Ac2 +                   
            self.Ac1 @ X @ S_c2_tilde @ self.Ac2.T @ S_c2_tilde +
            self.Ac1.T @ X @ S_c2_tilde @ self.Ac2 @ S_c2_tilde                       
        )

        gradY_topo = -self.lambda_tL * (
            S_l1_tilde @ self.Al1 @ S_l1_tilde @ Y @ self.Al2.T + 
            S_l1_tilde @ self.Al1.T @ S_l1_tilde @ Y @ self.Al2 +                   
            self.Al1 @ Y @ S_l2_tilde @ self.Al2.T @ S_l2_tilde +
            self.Al1.T @ Y @ S_l2_tilde @ self.Al2 @ S_l2_tilde                       
        )

        # gradX_cross = -self.lambda_c * (self.Acl1 @ Y @ self.Acl2.T)
        # gradY_cross = -self.lambda_c * (self.Acl1.T @ X @ self.Acl2)
        gradX_cross = -self.lambda_c * (
            S_c1_tilde @ self.Acl1_left @ S_l1_tilde @ Y @ self.Acl2_left.T + (S_c2_tilde @ self.Acl2_left @ S_l2_tilde @ Y.T @ self.Acl1_left.T).T +
            S_c1_tilde @ self.Acl1_right @ S_l1_tilde @ Y @ self.Acl2_right.T + (S_c2_tilde @ self.Acl2_right @ S_l2_tilde @ Y.T @ self.Acl1_right.T).T
        )

        gradY_cross = -self.lambda_c * (
            S_l1_tilde @ self.Acl1_left.T @ S_c1_tilde @ X @ self.Acl2_left + (S_l2_tilde @ self.Acl2_left.T @ S_c2_tilde @ X.T @ self.Acl1_left).T + 
            S_l1_tilde @ self.Acl1_right.T @ S_c1_tilde @ X @ self.Acl2_right + (S_l2_tilde @ self.Acl2_right.T @ S_c2_tilde @ X.T @ self.Acl1_right).T
        )

        mode_gradX = {
            "geom": gradX_geom,
            "topo": gradX_topo,
            "geom-topo": gradX_geom + gradX_topo,
            "fusion-base": gradX_geom + gradX_topo + gradX_cross,
            "fusion": gradX_geom + gradX_topo + gradX_cross
        }
        mode_gradY = {
            "geom": gradY_geom,
            "topo": gradY_topo,
            "geom-topo": gradY_geom + gradY_topo,
            "fusion-base": gradY_geom + gradY_topo + gradY_cross,
            "fusion": gradY_geom + gradY_topo + gradY_cross
        }
        gradX = mode_gradX[self.mode]
        gradY = mode_gradY[self.mode]

        if self.reduce_bool:
            gradX_extracted = np.zeros(len(self.I['x']))
            gradY_extracted = np.zeros(len(self.I['y']))
            for i in range(len(self.I['x'])):
                gradX_extracted[i] = gradX[self.I['x'][i], self.J['x'][i]]
            
            for i in range(len(self.I['y'])):
                gradY_extracted[i] = gradY[self.I['y'][i], self.J['y'][i]]
            return np.concatenate((gradX_extracted, gradY_extracted))
        else:
            return np.concatenate((gradX.ravel(), gradY.ravel()))
    
    def constraints(self, x):
        return self.Aeq @ x - self.beq
    
    def jacobian(self, x):
        return self.Aeq.data
    
    def jacobianstructure(self):
        return self.Aeq.nonzero()
