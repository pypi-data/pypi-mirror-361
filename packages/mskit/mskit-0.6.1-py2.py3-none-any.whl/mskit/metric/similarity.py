import numpy as np
from scipy.stats import pearsonr


def pcc(data1, data2, keep_pvalue=False):
    p = pearsonr(data1, data2)
    if keep_pvalue:
        return p
    else:
        return p[0]


def sa(data1, data2):
    """
    Calculates the spectral angle similarity between two data arrays.

    Parameters:
    data1 (array-like): The first data array.
    data2 (array-like): The second data array.

    Returns:
    float: The spectral angle similarity between the two data arrays.
    """
    data1 = np.array(data1)
    data2 = np.array(data2)
    norm_data1 = data1 / np.sqrt(sum(np.square(data1)))
    norm_data2 = data2 / np.sqrt(sum(np.square(data2)))
    s = 1 - 2 * (np.arccos(sum(norm_data1 * norm_data2))) / np.pi
    return s
