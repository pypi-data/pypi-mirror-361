import numpy as np


__all__ = [
    "delta_tx_to_rt_2diff",
    "rt_diff_to_delta_tx",
    "delta_tx",
    "r_square",
]


def delta_tx_to_rt_2diff(obse, pred, percent):
    # np.percentile(np.sort(np.abs(obse - pred)), percent) * 2
    num_x = int(np.ceil(len(obse) * percent / 100))
    return 2 * sorted(abs(np.array(obse) - np.array(pred)))[num_x - 1]


def rt_diff_to_delta_tx(obse, pred, oneside_diff):
    deviation = np.sort(abs(np.array(obse) - np.array(pred)))
    if oneside_diff >= deviation[-1]:
        return 100
    else:
        idx = np.where(deviation > oneside_diff)[0][0]
        return idx / len(obse) * 100


delta_tx = delta_tx_to_rt_2diff


def r_square(obse, pred):
    obse = np.array(obse)
    pred = np.array(pred)
    sse = np.sum(np.square(pred - obse))
    sst = np.sum(np.square(pred - np.mean(obse)))
    r_2 = 1 - sse / sst
    return r_2
