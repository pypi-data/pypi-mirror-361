import typing

import numpy as np
import pandas as pd

from mskit import multi_kits as rk

__all__ = [
    "assemble_topn",
    "apply_assemble_topn",
    "norm_quant_by_ref",
]


def assemble_topn(
    values: typing.Union[list, tuple, np.ndarray, pd.Series],
    topn: typing.Union[int, None, bool] = 3,
    assemble_func: typing.Union[str, typing.Callable] = np.mean,
    nan_value=np.nan,
    thres: typing.Union[int, float, np.ndarray, pd.Series] = 10,
):
    """
    :param values:

    :param topn:
        int to keep top n items or True for top 3, or others with no action
    :param assemble_func:

    :param nan_value:

    :param thres:

    """
    values = np.asarray(values)
    if isinstance(thres, (int, float, np.ndarray, pd.Series)):
        values = values[values > thres]
    elif thres is True:
        values = values[values > 1]

    if len(values) == 0:
        return nan_value
    if isinstance(topn, bool):
        topn = 3 if topn else 0
    if isinstance(topn, int) and topn >= 1:
        values = np.sort(values)[::-1][:topn]

    if isinstance(assemble_func, str):
        if assemble_func.lower() in (
            "mean",
            "nanmean",
            "np.mean",
            "np.nanmean",
        ):
            assemble_func = np.nanmean
        elif assemble_func.lower() in (
            "median",
            "nanmedian",
            "np.median",
            "np.nanmedian",
        ):
            assemble_func = np.nanmedian
        elif assemble_func.lower() in (
            "sum",
            "nansum",
            "np.sum",
            "np.nansum",
        ):
            assemble_func = np.nansum
        else:
            raise ValueError(
                f"`assemble_func` should be callable object or string. When is string, should be one of `mean`, `median`, or `sum`"
            )

    return assemble_func(values)


def apply_assemble_topn(
    df: pd.DataFrame,
    group_cols=("Cond", "Rep", "ProteinGroup"),
    low_level_quant_col: str = "FG.Quantity",
    assemble_quant_colname: str = "ProtQuant",
    dask_npart: int = None,
    **kwargs,
) -> pd.DataFrame:
    """

    :param df: pandas DataFrame
        Only pandas df is valid and dask df is not fine, since the index of dask dataframe may not be unique for assigning new column
    :param group_cols:

    :param low_level_quant_col:

    :param assemble_quant_colname:

    :param dask_npart:

    :return:
    """
    if dask_npart is not None:
        from dask import dataframe as dd
        
        raw_idx_col = rk.get_random_string(exclude=df.columns.tolist())
        raw_idx_name = df.index.name
        df[raw_idx_col] = df.index.values.copy()
        df = df.reset_index(drop=True)

        ddf = dd.from_pandas(df, npartitions=dask_npart)
        df[assemble_quant_colname] = (
            ddf.groupby(list(group_cols))[low_level_quant_col]
            .transform(assemble_topn, **kwargs, meta=(low_level_quant_col, "float"))
            .compute()
            .loc[df.index]
        )
        df.index = df[raw_idx_col].values
        df.index = df.index.rename(raw_idx_name)
        df = df.drop(columns=raw_idx_col)
    else:
        df[assemble_quant_colname] = df.groupby(list(group_cols))[low_level_quant_col].transform(
            assemble_topn, **kwargs
        )
    return df


def norm_quant_by_ref(
    df: pd.DataFrame,
    run_colname="R.FileName",
    quant_colname="FG.Quantity",
    ref_run_name="Ref",
    norm_type="median",
) -> pd.Series:
    if isinstance(ref_run_name, str):
        ref_run_name = [ref_run_name]
    if norm_type.lower() == "median":
        ref_run_median_quant = (
            df[df[run_colname].isin(ref_run_name)].groupby(run_colname)[quant_colname].median().median()
        )
        _func = np.nanmedian
    elif norm_type.lower() == "sum":
        ref_run_median_quant = df[df[run_colname].isin(ref_run_name)].groupby(run_colname)[quant_colname].sum().median()
        _func = np.nansum
    else:
        raise ValueError(f"")
    return df[quant_colname] / df.groupby(run_colname)[quant_colname].transform(_func) * ref_run_median_quant
