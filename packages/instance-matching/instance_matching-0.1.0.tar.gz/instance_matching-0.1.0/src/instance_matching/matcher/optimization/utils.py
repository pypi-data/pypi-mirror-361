import numpy as np
from scipy.sparse import issparse

def remove_end_end(i, j, shape):
    m, n = shape
    return i[~((i == m - 1) & (j == n - 1))], j[~((i == m - 1) & (j == n - 1))]

def trace(A):
    if issparse(A):
        return A.diagonal().sum()
    else:
        return np.trace(A)
    
def convert_adjacency_matrix(A):
        m, n = A.shape
        A_tilde =  2 * A - np.ones((m, n))
        A_tilde[-1, :] = 0
        A_tilde[:, -1] = 0
        return A_tilde
