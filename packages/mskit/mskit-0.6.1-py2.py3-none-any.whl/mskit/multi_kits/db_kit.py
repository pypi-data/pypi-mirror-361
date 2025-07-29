"""
All functions with returned values in this module will return at least two variance, and the first one must be a connection instance of database
"""

import sqlite3

import pandas as pd


def get_sqlite_cursor(db) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    if isinstance(db, sqlite3.Connection):
        return db, db.cursor()
    elif isinstance(db, sqlite3.Cursor):
        return db.connection, db
    elif isinstance(db, str):
        con = sqlite3.connect(db)
        return con, con.cursor()
    else:
        raise ValueError(
            f"Parameter `db` should be a connection, or a cursor, or the path of a sqlite database file. Now {type(db)=} - {db}"
        )


def get_sqlite_table_title(db, table_name: str, keep_meta: bool = False) -> tuple[sqlite3.Connection, list]:
    con, cur = get_sqlite_cursor(db)
    table_title = cur.execute(f"PRAGMA table_info({table_name})").fetchall()
    if not keep_meta:
        table_title = [_[1] for _ in table_title]
    return con, table_title


def load_one_sqlite_table(db, table_name, table_title=None) -> tuple[sqlite3.Connection, pd.DataFrame]:
    con, cur = get_sqlite_cursor(db)
    if table_title is None:
        _, table_title = get_sqlite_table_title(cur, table_name=table_name, keep_meta=False)
    df = pd.DataFrame(cur.execute(f"SELECT * FROM {table_name}").fetchall(), columns=table_title)
    return con, df


def load_sqlite_master_table(db, only_keep_table_info: bool = False) -> tuple[sqlite3.Connection, pd.DataFrame]:
    con, df = load_one_sqlite_table(db, table_name="sqlite_master", table_title=None)
    if only_keep_table_info:
        df = df[df["type"] == "table"].copy()
    return con, df


def load_all_sqlite_tables(db, close_db: bool = False) -> tuple[sqlite3.Connection, dict[str, pd.DataFrame]]:
    con, df = load_sqlite_master_table(db, only_keep_table_info=True)
    tables = {
        table_name: load_one_sqlite_table(con, table_name=table_name, table_title=None)[1]
        for table_name in df["name"].values
    }
    if close_db:
        con.close()
    return con, tables
