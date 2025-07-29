import typing

from mskit import multi_kits as rk


def check_rt_table_correction(blib_path):
    con, cur = rk.get_sqlite_cursor(blib_path)

    blib_tables = dict()
    try:
        for name in ["RetentionTimes", "RefSpectra", "IrtLibrary"]:
            _, blib_tables[name] = rk.load_one_sqlite_table(cur, table_name=name)
            print(name, f"Table nrows: {len(blib_tables[name])}")
    finally:
        con.close()

    modpep_in_spec_notin_rt = blib_tables["RefSpectra"][
        ~blib_tables["RefSpectra"]["id"].isin(
            blib_tables["RetentionTimes"][
                ("RefSpectraID" if "RefSpectraID" in blib_tables["RetentionTimes"].columns else "RefSpectraId")
            ].values
        )
    ]
    print("Modified peptides in RefSpectra table but not in RetentionTimes table:", modpep_in_spec_notin_rt)

    modpep_in_spec_notin_irt = set(blib_tables["RefSpectra"]["peptideModSeq"]) - set(
        [
            _.replace("[+42.010565]", "[+42.01056]")
            .replace("[+57.021464]", "[+57.02146]")
            .replace("[+15.994915]", "[+15.99492]")
            .replace("[+79.966331]", "[+79.96633]")
            .replace("[+99.032029]", "[+99.03203]")
            for _ in set(blib_tables["IrtLibrary"]["PeptideModSeq"])
        ]
    )
    print("Modified peptides in RefSpectra table but not in IrtLibrary table:", modpep_in_spec_notin_irt)

    return blib_tables


def skyline_int5modpep_to_unimodpep(x):
    if "[+42.01056]" in x:
        x = f'(UniMod:1){x.replace("[+42.01056]", "")}'
    if x.startswith("C[+99.03203]"):
        x = f'(UniMod:1){x.replace("C[+99.03203]", "C(UniMod:4)")}'
    x = x.replace("[+57.02146]", "(UniMod:4)")
    x = x.replace("[+79.96633]", "(UniMod:21)")
    x = x.replace("[+15.99492]", "(UniMod:35)")
    return x


def add_im_to_blib(
    blib_path: str,
    prec_to_im_map: dict,
    skyline_intmodpep_to_input_modpep_map: typing.Union[dict, typing.Callable] = None,
    close_sqlite_session=True,
):
    """
    :param blib_path
    :param prec_to_im_map: dict with keys as ('UniModPep', PrecCharge), values as IM value (float),
                           like {('M(UniMod:35)GVFSSR', 2): 0.7365193627394048, ...}
    :param skyline_intmodpep_to_input_modpep_map:
    :param close_sqlite_session:

    Maybe need to check if table IonMobilityTypes existed or
    "CREATE TABLE IF NOT EXISTS IonMobilityTypes"
    cur.execute("SELECT id FROM IonMobilityTypes WHERE ionMobilityType = 'inveseK0(Vsec/cm^2)'").fetchall()

    """
    con, cur = rk.get_sqlite_cursor(blib_path)

    sql_create_im_table = """
        CREATE TABLE IonMobilityTypes 
        (id integer primary key autoincrement, ionMobilityType TEXT);
        INSERT INTO IonMobilityTypes VALUES (0, 'none');
        INSERT INTO IonMobilityTypes VALUES (1, 'driftTime(msec)');
        INSERT INTO IonMobilityTypes VALUES (2, 'inverseK0(Vsec/cm^2)');
        INSERT INTO IonMobilityTypes VALUES (3, 'compensation(V)');
        """
    print("Execte:\n", sql_create_im_table)
    cur.executescript(sql_create_im_table)
    con.commit()

    sql_get_all_from_refspec_table = "SELECT * FROM RefSpectra"
    print("Execte:\n", sql_get_all_from_refspec_table)
    cur.execute(sql_get_all_from_refspec_table)
    table_content = cur.fetchall()

    sql_delete_all_in_refspec_table = "DELETE FROM RefSpectra"
    print("Execte:\n", sql_delete_all_in_refspec_table)
    cur.execute(sql_delete_all_in_refspec_table)
    con.commit()

    table_content = [list(c) for c in table_content]
    im_not_found_count = 0
    for i, c in enumerate(table_content):
        modpep, charge = c[2], c[3]
        if skyline_intmodpep_to_input_modpep_map is None:
            modpep = skyline_int5modpep_to_unimodpep(modpep)
        elif skyline_intmodpep_to_input_modpep_map is False:
            pass
        elif isinstance(skyline_intmodpep_to_input_modpep_map, dict):
            modpep = skyline_intmodpep_to_input_modpep_map[modpep]
        else:
            modpep = skyline_intmodpep_to_input_modpep_map(modpep)

        _value = prec_to_im_map.get((modpep, charge))
        if _value is None:
            im_not_found_count += 1

        table_content[i][14] = _value
        table_content[i][17] = 2

    sql_fill_in_refspec_table = f"INSERT INTO RefSpectra VALUES ({', '.join(['?'] * 23)})"
    print("Execte:\n", sql_fill_in_refspec_table)
    cur.executemany(sql_fill_in_refspec_table, table_content)
    con.commit()

    sql_fill_other_im_values_in_refspec_table = """
        UPDATE RefSpectra SET collisionalCrossSectionSqA = 0;
        UPDATE RefSpectra SET ionMobilityHighEnergyOffset = 0;
        """
    print("Execte:\n", sql_fill_other_im_values_in_refspec_table)
    cur.executescript(sql_fill_other_im_values_in_refspec_table)
    con.commit()

    sql_update_rt_table_im_info = """
        UPDATE RetentionTimes SET ionMobility = (SELECT ionMobility FROM RefSpectra WHERE RetentionTimes.RefSpectraId = RefSpectra.id);
        UPDATE RetentionTimes SET collisionalCrossSectionSqA = 0;
        UPDATE RetentionTimes SET ionMobilityHighEnergyOffset = 0;
        UPDATE RetentionTimes SET ionMobilityType = 2;
        """
    print("Execte:\n", sql_update_rt_table_im_info)
    cur.executescript(sql_update_rt_table_im_info)
    con.commit()

    if close_sqlite_session:
        con.close()
        return None
    else:
        return con


class BlibConstTableValues:
    ScoreTypes = """
        INSERT INTO ScoreTypes VALUES (0, 'UNKNOWN', 'NOT_A_PROBABILITY_VALUE');
        INSERT INTO ScoreTypes VALUES (1, 'PERCOLATOR QVALUE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (2, 'PEPTIDE PROPHET SOMETHING', 'PROBABILITY_THAT_IDENTIFICATION_IS_CORRECT');
        INSERT INTO ScoreTypes VALUES (3, 'SPECTRUM MILL', 'NOT_A_PROBABILITY_VALUE');
        INSERT INTO ScoreTypes VALUES (4, 'IDPICKER FDR', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (5, 'MASCOT IONS SCORE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (6, 'TANDEM EXPECTATION VALUE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (7, 'PROTEIN PILOT CONFIDENCE', 'PROBABILITY_THAT_IDENTIFICATION_IS_CORRECT');
        INSERT INTO ScoreTypes VALUES (8, 'SCAFFOLD SOMETHING', 'PROBABILITY_THAT_IDENTIFICATION_IS_CORRECT');
        INSERT INTO ScoreTypes VALUES (9, 'WATERS MSE PEPTIDE SCORE', 'NOT_A_PROBABILITY_VALUE');
        INSERT INTO ScoreTypes VALUES (10, 'OMSSA EXPECTATION SCORE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (11, 'PROTEIN PROSPECTOR EXPECTATION SCORE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (12, 'SEQUEST XCORR', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (13, 'MAXQUANT SCORE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (14, 'MORPHEUS SCORE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (15, 'MSGF+ SCORE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (16, 'PEAKS CONFIDENCE SCORE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (17, 'BYONIC SCORE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        INSERT INTO ScoreTypes VALUES (18, 'PEPTIDE SHAKER CONFIDENCE', 'PROBABILITY_THAT_IDENTIFICATION_IS_CORRECT');
        INSERT INTO ScoreTypes VALUES (19, 'GENERIC Q-VALUE', 'PROBABILITY_THAT_IDENTIFICATION_IS_INCORRECT');
        """

    IonMobilityTypes = """
        INSERT INTO IonMobilityTypes VALUES (0, 'none');
        INSERT INTO IonMobilityTypes VALUES (1, 'driftTime(msec)');
        INSERT INTO IonMobilityTypes VALUES (2, 'inverseK0(Vsec/cm^2)');
        INSERT INTO IonMobilityTypes VALUES (3, 'compensation(V)');
        """
