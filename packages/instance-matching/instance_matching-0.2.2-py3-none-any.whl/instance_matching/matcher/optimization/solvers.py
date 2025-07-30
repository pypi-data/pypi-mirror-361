import numpy as np
import cyipopt
from typing import Tuple
from .problem import OptimizationProblem
from .utils import remove_end_end

def solve_initial_geom(
    Cc: np.ndarray,
    Cl: np.ndarray,
    Ac1: np.ndarray,
    Ac2: np.ndarray,
    Al1: np.ndarray,
    Al2: np.ndarray,
    Acl1_left: np.ndarray,
    Acl1_right: np.ndarray,
    Acl2_left: np.ndarray,
    Acl2_right: np.ndarray,
    padding_cost: float,
    weights: list,
    precompute: bool = False,
    matrices: dict = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Solve the geometry‐only reduced problem via IPOPT to get initial X, Y.

    Returns:
        X_init: (n1+1)x(n2+1) matching matrix for center‐lines.
        Y_init: (n3+1)x(n4+1) matching matrix for lane‐dividers.
    """
    # dimensions
    n1 = Cc.shape[0] - 1
    n2 = Cc.shape[1] - 1
    n3 = Cl.shape[0] - 1
    n4 = Cl.shape[1] - 1

    # variable counts
    num_x = (n1 + 1)*(n2 + 1)
    num_y = (n3 + 1)*(n4 + 1)
    n_vars = num_x + num_y
    n_cons = n1 + n2 + n3 + n4

    # bounds
    lb = [0.0]*n_vars
    ub = [1.0]*n_vars
    cl = [0.0]*n_cons
    cu = [0.0]*n_cons

    # initial guess
    x0 = np.random.rand(n_vars)

    # sparse_params unused for full problem
    i_x, j_x = np.where(Cc <= padding_cost)
    i_y, j_y = np.where(Cl <= padding_cost)

    sparse_params = {'Ix': None, 'Iy': None, 'Jx': None, 'Jy': None}
    sparse_params['Ix'], sparse_params['Iy'] = remove_end_end(i_x, j_x, Cc.shape)
    sparse_params['Iy'], sparse_params['Jy'] = remove_end_end(i_y, j_y, Cl.shape)

    matrix_params = {
        'Cc': Cc, 'Cl': Cl,
        'Ac1': Ac1, 'Ac2': Ac2,
        'Al1': Al1, 'Al2': Al2,
        'Acl1_left': Acl1_left, 'Acl1_right': Acl1_right,
        'Acl2_left': Acl2_left, 'Acl2_right': Acl2_right
    }

    # construct and solve
    problem = cyipopt.Problem(
        n=n_vars,
        m=n_cons,
        problem_obj=OptimizationProblem(
            n_vars, n_cons, "geom", False,
            sparse_params, matrix_params,
            {'params': {'weights': weights, 'padding_cost': padding_cost}, 'precompute': precompute}
        ),
        lb=lb, ub=ub, cl=cl, cu=cu
    )
    problem.add_option('print_level', 0)
    x_opt, _ = problem.solve(x0)

    X_init = x_opt[:num_x].reshape(n1+1, n2+1)
    Y_init = x_opt[num_x:].reshape(n3+1, n4+1)
    return X_init, Y_init

def solve_matching_method(
    method: str,
    X_init: np.ndarray,
    Y_init: np.ndarray,
    Cc: np.ndarray,
    Cl: np.ndarray,
    Ac1: np.ndarray,
    Ac2: np.ndarray,
    Al1: np.ndarray,
    Al2: np.ndarray,
    Acl1_left: np.ndarray,
    Acl1_right: np.ndarray,
    Acl2_left: np.ndarray,
    Acl2_right: np.ndarray,
    padding_cost: float,
    weights: list,
    use_reduced: bool
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Solve one matching method via IPOPT, optionally with variable reduction.
    """
    n1 = Cc.shape[0] - 1
    n2 = Cc.shape[1] - 1
    n3 = Cl.shape[0] - 1
    n4 = Cl.shape[1] - 1

    i_x, j_x = np.where(Cc <= padding_cost)
    i_y, j_y = np.where(Cl <= padding_cost)
    sparse_params = {'Ix': None, 'Iy': None, 'Jx': None, 'Jy': None}
    sparse_params['Ix'], sparse_params['Jx'] = remove_end_end(i_x, j_x, Cc.shape)
    sparse_params['Iy'], sparse_params['Jy'] = remove_end_end(i_y, j_y, Cl.shape)

    if use_reduced:
        # count reduced variables from X_init/Y_init
        # here we simply reuse full count for simplicity
        n_vars = len(sparse_params['Ix']) + len(sparse_params['Iy'])
        X_sample = np.zeros(len(sparse_params['Ix']))
        Y_sample = np.zeros(len(sparse_params['Iy']))

        for i in range(len(X_sample)):
            X_sample[i] = X_init[sparse_params['Ix'][i], sparse_params['Jx'][i]]

        for i in range(len(Y_sample)):
            Y_sample[i] = Y_init[sparse_params['Iy'][i], sparse_params['Jy'][i]]
        
        # x0 = np.concatenate((X_sample, Y_sample))
    else:
        n_vars = (n1+1)*(n2+1) + (n3+1)*(n4+1)
        # x0 = np.concatenate((X_init.ravel(), Y_init.ravel()))
    
    x0 = np.random.rand(n_vars)
    n_cons = n1 + n2 + n3 + n4

    lb = [0.0]*n_vars
    ub = [1.0]*n_vars
    cl = [0.0]*n_cons
    cu = [0.0]*n_cons
    
    matrix_params = {
        'Cc': Cc, 'Cl': Cl,
        'Ac1': Ac1, 'Ac2': Ac2,
        'Al1': Al1, 'Al2': Al2,
        'Acl1_left': Acl1_left, 'Acl1_right': Acl1_right,
        'Acl2_left': Acl2_left, 'Acl2_right': Acl2_right
    }

    problem = cyipopt.Problem(
        n=n_vars,
        m=n_cons,
        problem_obj=OptimizationProblem(
            n_vars, n_cons, method, use_reduced,
            sparse_params, matrix_params,
            {'params': {'weights': weights, 'padding_cost': padding_cost}, 'precompute': False}
        ),
        lb=lb, ub=ub, cl=cl, cu=cu
    )
    problem.add_option('print_level', 0)
    problem.add_option('file_print_level', 0)
    problem.add_option('max_iter', 100)
    x_opt, _ = problem.solve(x0)

    if use_reduced:
        X_sample = x_opt[:len(sparse_params['Ix'])]
        Y_sample = x_opt[len(sparse_params['Ix']):]
        X = np.zeros((n1+1, n2+1))
        Y = np.zeros((n3+1, n4+1))
        X[sparse_params['Ix'], sparse_params['Jx']] = X_sample
        Y[sparse_params['Iy'], sparse_params['Jy']] = Y_sample
    else:
        num_x = (n1+1)*(n2+1)
        X = x_opt[:num_x].reshape(n1+1, n2+1)
        Y = x_opt[num_x:].reshape(n3+1, n4+1)
        
    return X, Y
