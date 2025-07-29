import sqlite3

import pandas as pd
from mskit import multi_kits as rk


def get_osw_feature_table(path) -> pd.DataFrame:
    con = sqlite3.connect(path)
    cur = con.cursor()
    try:
        _, prec_table = rk.load_one_sqlite_table(cur, table_name="PRECURSOR")
        _, feature_table = rk.load_one_sqlite_table(cur, table_name="FEATURE")
    finally:
        con.close()

    feature_table["RT_in_Minutes"] = feature_table["EXP_RT"] / 60
    feature_table["DECOY"] = feature_table["PRECURSOR_ID"].map(dict(prec_table[["ID", "DECOY"]].values))
    return feature_table
