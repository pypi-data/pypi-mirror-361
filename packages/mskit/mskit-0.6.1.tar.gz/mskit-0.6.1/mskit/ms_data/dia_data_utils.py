import numpy as np
import pandas as pd
from tqdm import tqdm

__all__ = [
    "extract_dia_window_mzml",
    "extract_tic_raw",
]


def extract_dia_window_mzml(
    mzml_file,
    cut_overlap_at_half: bool = False,
    half_overlap_as_margin: bool = False,
    columns=("lower_offset", "upper_offset", "margin"),
    max_iter_spec_num: int = 150,
    sort: bool = True,
    drop_duplicates: bool = True,
) -> pd.DataFrame:
    try:
        import pymzml

        dia_windows = []
        start_record = False
        with pymzml.run.Reader(mzml_file) as mzml:
            for idx, spec in enumerate(mzml):
                if spec.ms_level == 1:
                    if start_record:
                        used_cols = columns[:2]
                        window_df = pd.DataFrame(dia_windows, columns=used_cols)
                        if drop_duplicates:
                            window_df = window_df.drop_duplicates(used_cols)
                        if sort:
                            window_df = window_df.sort_values(list(used_cols))
                        return window_df
                    else:
                        start_record = True
                elif spec.ms_level == 2:
                    if start_record:
                        dia_windows.append(
                            (
                                spec.selected_precursors[0]["mz"] - spec["MS:1000828"],
                                spec.selected_precursors[0]["mz"] + spec["MS:1000829"],
                            )
                        )
                else:
                    pass  # OR Raise
                if idx > max_iter_spec_num:
                    if start_record:
                        raise ValueError(f"Iterate mzml file for {max_iter_spec_num} spectra but no further MS1 appear")
                    else:
                        raise ValueError(
                            f"Iterate mzml file for {max_iter_spec_num} spectra but no MS1 spectrum appear"
                        )
    except ModuleNotFoundError:
        # import pyteomics
        raise ModuleNotFoundError("pymzml is not installed.")


def extract_tic_raw(msfile, out_file, sep="\t"):
    try:
        import pymsfilereader
    except ModuleNotFoundError:
        raise ModuleNotFoundError("pymsfilereader is not installed.")

    msfile = pymsfilereader.MSFileReader(msfile)
    try:
        spec_num = msfile.GetNumSpectra()
        print(f"Spectrum number: {spec_num}")
        with tqdm(range(1, spec_num + 1)) as t, open(out_file, "w") as f:
            f.write(
                sep.join(["SpecNum", "MSOrder", "RecordSignalNum", "NonZeroSignalNum", "SummedSignal", "Min", "Max"])
            )
            f.write("\n")
            for spec_idx in t:
                ms_order = msfile.GetMSOrderForScanNum(spec_idx)
                intens = np.array(msfile.GetMassListFromScanNum(spec_idx)[0][1])
                f.write(
                    sep.join(
                        map(
                            str,
                            [
                                spec_idx,
                                ms_order,
                                len(intens),
                                (intens > 0.5).sum(),
                                np.sum(intens),
                                np.min(intens),
                                np.max(intens),
                            ],
                        )
                    )
                )
                f.write("\n")
    finally:
        msfile.Close()
