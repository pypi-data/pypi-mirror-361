import re
import typing

import numpy as np
import pandas as pd
import dask.dataframe as dd

from mskit import multi_kits as rk
from mskit.calc import calc_ion_mz


def tsvlib_to_mqlib(
    tsv_lib: typing.Union[str, pd.DataFrame],
    output_folder: str,
    create_folder_with_tsv_filename: bool = True,
    modpep_col: str = "ModifiedPeptideSequence",
    logger=None,
):
    if isinstance(tsv_lib, str):
        tsv_lib = pd.read_csv(tsv_lib, sep="\t")
    elif isinstance(tsv_lib, pd.DataFrame):
        pass
    else:
        raise ValueError(f"Input tsv library should be either a path or a dataframe. Now {type(tsv_lib)}")

    if logger is not None:
        logger.info("Transforming modified peptide format in tsv library")
    tsv_lib["ModPep-MQStyle"] = tsv_lib[modpep_col].apply()


def convert_tsv_spec_to_mq(x, recalc_mz: bool = False):
    modpep = x["ModifiedPeptideSequence"].iloc[0]
    ion_name = []
    intens = []

    if recalc_mz:
        ion_type, ion_seriesnum, ion_loss, ion_charge = [], [], [], []

        for i_t, i_sn, i_c, i_l, i_inten in x[
            ["FragmentType", "FragmentSeriesNumber", "FragmentCharge", "FragmentLossType", "LibraryIntensity"]
        ].values:
            if i_c == 1:
                ion_name.append(f"{i_t}{i_sn}" if i_l.lower() == "noloss" else f"{i_t}{i_sn}-{i_l}")
            elif i_c == 2 and i_l.lower() == "noloss":
                ion_name.append(f"{i_t}{i_sn}(2+)")
            else:
                continue
            ion_type.append(i_t)
            ion_seriesnum.append(i_sn)
            ion_loss.append(i_l)
            ion_charge.append(i_c)
            intens.append(i_inten)

        ion_mzs = calc_ion_mz(
            modpep,
            ion_charge,
            ion_type=ion_type,
            ion_series_num=ion_seriesnum,
            ion_loss_type=ion_loss,
            mod_mould="(",
            c_with_fixed_mod=False,
            pep_preprocess_func=None,
            return_single_value_if_one_input=False,
        )
    else:
        ion_mzs = []

        for i_t, i_sn, i_c, i_l, i_mz, i_inten in x[
            [
                "FragmentType",
                "FragmentSeriesNumber",
                "FragmentCharge",
                "FragmentLossType",
                "ProductMz",
                "LibraryIntensity",
            ]
        ].values:
            if i_c == 1:
                ion_name.append(f"{i_t}{i_sn}" if i_l.lower() == "noloss" else f"{i_t}{i_sn}-{i_l}")
            elif i_c == 2 and i_l.lower() == "noloss":
                ion_name.append(f"{i_t}{i_sn}(2+)")
            else:
                continue
            ion_mzs.append(i_mz)
            intens.append(i_inten)

    if len(ion_name) < 3:
        return None

    return ion_name, ion_mzs, np.asarray(intens) / np.max(intens) * 10000


TIMS_TSVLib["FragmentLossType"] = TIMS_TSVLib["FragmentLossType"].fillna("noloss")
TIMS_TSVLib["Prec"] = TIMS_TSVLib["Modified sequence"] + TIMS_TSVLib["Charge"].astype(str)
TIMS_TSVLib = TIMS_TSVLib.sort_values(
    ["Prec", "FragmentType", "FragmentSeriesNumber", "FragmentCharge"],
    ascending=[True, False, True, True],
    kind="mergesort",
)

r = TIMS_TSVLib.groupby("Prec").apply(convert_tsv_spec_to_mq)
prec_to_frag_names = dict([(prec, ";".join(items[0])) for prec, items in r.items() if items is not None])
prec_to_frag_masses = dict(
    [(prec, ";".join([str(_) for _ in items[1]])) for prec, items in r.items() if items is not None]
)
prec_to_frag_intens = dict(
    [(prec, ";".join([str(_) for _ in items[2]])) for prec, items in r.items() if items is not None]
)
print(f'Total precursors in tsv library: {len(set(TIMS_TSVLib["Prec"]))}')
print(f"Converted spec: {len(prec_to_frag_names)}")
