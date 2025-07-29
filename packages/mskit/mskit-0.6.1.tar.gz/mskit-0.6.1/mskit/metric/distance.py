import numpy as np
from scipy.spatial.distance import euclidean


def _c(ca, i, j, p, q):
    if ca[i, j] > -1:
        return ca[i, j]
    elif i == 0 and j == 0:
        ca[i, j] = euclidean(p[0], q[0])
    elif i > 0 and j == 0:
        ca[i, j] = max(_c(ca, i - 1, 0, p, q), euclidean(p[i], q[0]))
    elif i == 0 and j > 0:
        ca[i, j] = max(_c(ca, 0, j - 1, p, q), euclidean(p[0], q[j]))
    elif i > 0 and j > 0:
        ca[i, j] = max(
            min(_c(ca, i - 1, j, p, q), _c(ca, i - 1, j - 1, p, q), _c(ca, i, j - 1, p, q)), euclidean(p[i], q[j])
        )
    else:
        ca[i, j] = float("inf")
    return ca[i, j]


def frechet_dist(p, q):
    """
    Calculates the Frechet distance between two curves represented by points p and q.

    Parameters:
    p (numpy.ndarray): Array of points representing the first curve.
    q (numpy.ndarray): Array of points representing the second curve.

    Returns:
    float: The Frechet distance between the two curves.
    """
    ca = np.ones((len(p), len(q)))
    ca = np.multiply(ca, -1)
    return _c(ca, len(p) - 1, len(q) - 1, p, q)
