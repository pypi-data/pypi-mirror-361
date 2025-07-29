import numpy as np
import scipy.stats
import sklearn


def iqr(value: np.ndarray):
    return np.percentile(value, 75) - np.percentile(value, 25)


def cv(
    value_array: np.ndarray,
    min_quant_value_num=3,
    std_ddof=1,
    make_percentage=True,
    keep_na=False,
    decimal_place=None,
    return_iqr=False,
):
    """
    :param value_array: A two-dimensional array with rows as sample and cols as replicates. CV will be performed to each row (dim 0)
    :param min_quant_value_num: Minimum number of non-NA values
    :param std_ddof: ddof for std
    :param make_percentage: If true, CVs will be multi with 100, else nothing will do. Default True
    :param keep_na: Whether to return NAs for those CV-unavailable samples. If True, the returned CVs will have the same size as input samples. Default False
    :param decimal_place:
    :param return_iqr: Whether to return IQR of calulated CVs. If True, a tuple like (cvs, iqr) will be returned, otherwise cvs only. Default False
    """
    if len(value_array.shape) != 2:
        raise ValueError(
            f"Expect a two-dim array to calc CV with sample as rows and replicates as cols. "
            f"Current input array has shape {value_array.shape} with {len(value_array.shape)} dim"
        )
    value_array = np.asarray(value_array)
    sample_num, rep_num = value_array.shape
    if min_quant_value_num > rep_num:
        min_quant_value_num = rep_num
    cv_avail_value_idx = np.where((rep_num - np.isnan(value_array).sum(axis=1)) >= min_quant_value_num)[0]
    cv_avail_values = value_array[cv_avail_value_idx]
    cvs = np.nanstd(cv_avail_values, axis=1, ddof=std_ddof) / np.nanmean(cv_avail_values, axis=1)
    if make_percentage:
        cvs = cvs * 100
    if keep_na:
        temp = np.zeros(sample_num)
        temp.fill(np.nan)
        temp[cv_avail_value_idx] = cvs
        cvs = temp.copy()
    return cvs


def count_missing_values(value_array: np.ndarray, keep_all_na_row=True):
    mvs = np.sum(np.isnan(value_array), axis=1)
    return mvs


def fwhm(values: np.ndarray, est_boundary=None, bound_expand_step=None, est_x_num=1e3):
    """
    :return: A tuple as (FWHM value, APEX point, estimated X, estimated Y, KDE func)
        FWHM will be None if half height can not be found in the range of input values two-side boundaries
    """
    sorted_values = np.sort(values)

    if est_boundary is not None:
        if len(est_boundary) != 2:
            raise ValueError
    else:
        est_boundary = (sorted_values[0], sorted_values[-1])

    kde = scipy.stats.kde.gaussian_kde(sorted_values)
    kde_x = np.linspace(*est_boundary, int(est_x_num))
    kde_y = kde(kde_x)
    apex_x_idx = np.argmax(kde_y)

    apex_left_half_height_x_idx = np.where(kde_y[:apex_x_idx] < kde_y[apex_x_idx] / 2)[0]
    if len(apex_left_half_height_x_idx) == 0:
        fwhm_min_idx = None
    else:
        fwhm_min_idx = apex_left_half_height_x_idx[-1]

    apex_right_half_height_x_idx = np.where(kde_y[apex_x_idx:] < kde_y[apex_x_idx] / 2)[0]
    if len(apex_right_half_height_x_idx) == 0:
        fwhm_max_idx = None
    else:
        fwhm_max_idx = apex_right_half_height_x_idx[0] + apex_x_idx

    apex_point = kde_x[apex_x_idx]
    if fwhm_min_idx is None or fwhm_max_idx is None:
        fwhm_value = None
    else:
        fwhm_value = kde_x[fwhm_max_idx] - kde_x[fwhm_min_idx]
    return fwhm_value, apex_point, kde_x, kde_y, kde


# def pca():
#     cond_quant_df = quant_df[conditions].dropna(how='any').copy()
#     pca_input_values = cond_quant_df.values.T
#     pca = sklearn.decomposition.PCA(n_components=2).fit(pca_input_values)
#     component_var = pca.explained_variance_ratio_
#     transformed_values = pca.transform(pca_input_values)
