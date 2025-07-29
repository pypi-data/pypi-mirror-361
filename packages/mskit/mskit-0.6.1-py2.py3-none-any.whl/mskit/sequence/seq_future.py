import re
from itertools import combinations
import typing

import pandas as pd
from tqdm import tqdm

from mskit import multi_kits as rk


def extract_kmer_seq_from_ptm_result(
    data: typing.Union[pd.DataFrame, list, tuple],
    ref_fasta: dict,
    around_n: int = 15,
    mod_mould: str = "(",
    target_mod: typing.Union[str, tuple, list] = None,
    df_modpep_col: str = "ModifiedPeptide",
    df_protein_col: str = "ProteinGroup",
    attach_mod_on_result_key: bool = False,
) -> dict:
    """

    :param data: DataFrame or list or tuple
        if df, two columns should be presented for modified peptide and protein group, and the column names should be given as two params
        if list or tuple, should be nested list/tuple, and each element should be like (modified_peptide, protein)
    :param ref_fasta:
    :param around_n: int
        number of extracted AAs on one-side
    :param mod_mould:
    :param target_mod:
    :param df_modpep_col: str
        the name of column for storing modified peptide if df is given
    :param df_protein_col:
        the name of column for storing protein if df is given
    :param attach_mod_on_result_key:

    :return: dict
        Keys: {modified_peptide}-{mod_pos_on_pep} or {modified_peptide}-{mod_pos_on_pep}_{mod_name}
        Values: Kmer-seq
    """

    if mod_mould in ["parentheses", "pare", "("]:
        mould_chars = ("(", ")")
    elif mod_mould in ["brackets", "square brackets", "medium brackets", "brac", "["]:
        mould_chars = ("[", "]")
    elif mod_mould in ["curly brackets", "curly", "{"]:
        mould_chars = ("{", "}")
    else:
        raise ValueError(f"Current value {mod_mould} for param `mod_mould` is not supported")
    target_mod = [target_mod] if isinstance(target_mod, str) else target_mod

    if isinstance(data, pd.DataFrame):
        data = data[[df_modpep_col, df_protein_col]].drop_duplicates(df_modpep_col).values

    modpep_to_kmerseq = dict()
    viewed_modpep_prot_pair = []
    for modpep, prot in data:
        if (modpep, prot) in viewed_modpep_prot_pair:
            continue

        prot_seq = ref_fasta.get(prot)
        if prot_seq is None:
            prot_seq = ref_fasta.get(prot.split(";")[0])
        if prot_seq is None:
            raise ValueError(
                f"Protein {prot} (has modified peptide {modpep}) can not be found in given reference FASTA"
            )

        stripped_pep, ext_pos, ext_mod = rk.find_substring(modpep, *mould_chars, keep_start_end_char=False)
        try:
            pep_pos_on_prot = prot_seq.index(stripped_pep) + 1
        except ValueError:
            raise ValueError(
                f"Peptide sequence {stripped_pep} can not match on protein {prot}. (original input ({modpep}, {prot}))"
            )

        for pos, mod in zip(ext_pos, ext_mod):
            if (target_mod is not None) and (mod not in target_mod):
                continue

            mod_pos_on_prot = pos + pep_pos_on_prot - 1

            if mod_pos_on_prot > around_n:
                prev_seq = prot_seq[mod_pos_on_prot - around_n - 1 : mod_pos_on_prot - 1]
            else:
                prev_seq = "_" * (around_n - mod_pos_on_prot + 1) + prot_seq[: mod_pos_on_prot - 1]

            back_seq = prot_seq[mod_pos_on_prot : mod_pos_on_prot + around_n]
            if len(back_seq) < around_n:
                back_seq = back_seq + "_" * (around_n - len(back_seq))

            k_mer_seq = f"{prev_seq}{prot_seq[mod_pos_on_prot - 1]}{back_seq}"
            if attach_mod_on_result_key:
                _result_key = f"{modpep}-{pos}_{mod}"
            else:
                _result_key = f"{modpep}-{pos}"

            modpep_to_kmerseq[_result_key] = k_mer_seq

        viewed_modpep_prot_pair.append((modpep, prot))
    return modpep_to_kmerseq


def extract_seq_window(seq, fasta_dict: dict, n=7, ex_pad_symbol="_"):
    """
    Iterate the whole provided fasta to first find all potential matched protein entry and positiosn, and extract all possiable results


    TODO fasta dict 可以传入 fasta parser
    TODO 可以指定蛋白序列 / 指定蛋白 acc
    """
    ext_data = []
    for acc, prot_seq in fasta_dict.items():
        if seq in prot_seq:
            find_pos = [_.span() for _ in re.finditer(seq, prot_seq)]
            for start_idx, end_pos in find_pos:
                if start_idx < n:
                    prev_seq = ex_pad_symbol * (n - start_idx) + prot_seq[:start_idx]
                else:
                    prev_seq = prot_seq[start_idx - n : start_idx]
                back_seq = prot_seq[end_pos : end_pos + n]
                if len(back_seq) < n:
                    back_seq = back_seq + ex_pad_symbol * (n - len(back_seq))
                ext_data.append((seq, prev_seq, back_seq, acc, start_idx + 1))
    return ext_data


def batch_extract_seq_window(seq_list, fasta_dict: dict, n=7, ex_pad_symbol="_", return_type="df"):
    extract_data = []
    not_find_data = []
    with tqdm(seq_list) as t:
        t.set_description(f"Extract seq window (n={n}): ")
        for seq in t:
            result = extract_seq_window(seq, fasta_dict=fasta_dict, n=n, ex_pad_symbol=ex_pad_symbol)
            if result:
                extract_data.extend(result)
            else:
                not_find_data.append(seq)
    if return_type == "raw":
        return extract_data, not_find_data
    elif return_type == "df":
        raw_df = pd.DataFrame(extract_data, columns=["Pep", "Prev", "Back", "Acc", "StartPos"])
        group_df = raw_df.groupby(["Pep", "Prev", "Back"]).apply(
            lambda x: ";".join(list(set(x["Acc"] + "-" + x["StartPos"].astype(str))))
        )
        group_df = group_df.reset_index()
        group_df.columns = ["Pep", "Prev", "Back", "Acc-PepPos"]
        return group_df, not_find_data
    else:
        raise ValueError(f'Return type should be one of the "raw" | "df", now {return_type}')


def batch_add_target_mod(pep_list, mod_type: dict = None, mod_processor=None):
    """
    TODO : This may result in some redundant results (dont know why)
    """
    modpep_list = []
    for pep in rk.drop_list_duplicates(pep_list):
        modpep_list.extend(add_target_mod(pep, mod_type, mod_processor))
    return rk.drop_list_duplicates(modpep_list)


def batch_add_target_charge(modpep_list, charge=(2, 3)):
    prec_list = []
    for modpep in rk.drop_list_duplicates(modpep_list):
        prec_list.extend(add_target_charge(modpep, charge))
    return prec_list


def add_target_mod(pep, mod_type: dict = None, mod_processor=None):
    """
    :param pep: target peptide
    :param mod_type: dict like {'Carbamidomethyl': -1, 'Oxidation': 1}
    where -1 means all possible AAs will be modified with the determined modification
    and an integer means the maximum number of this modification
    :param mod_processor: the mod add processor contains the standard mod rule or customed mod rule
    """
    if mod_type:
        mods = []
        for _mod, _num in mod_type.items():
            _standard_mod = mod_processor.get_standard_mod(_mod)
            possible_aa = mod_processor.query_possible_aa(_standard_mod)
            possible_site = sorted([_.end() for one_aa in possible_aa for _ in re.finditer(one_aa, pep)])
            possible_site_num = len(possible_site)
            if _num > possible_site_num:
                _num = possible_site_num
            if _num == 0 or possible_site_num == 0:
                continue
            elif _num == -1:
                mod = [[(_, _standard_mod) for _ in possible_site]]
            else:
                mod = [
                    [],
                ]
                for _i in range(1, _num + 1):
                    selected_site = [_ for _ in combinations(possible_site, _i)]
                    mod.extend(
                        [[(one_site, _standard_mod) for one_site in each_site_comb] for each_site_comb in selected_site]
                    )
            if mods:
                new_mod = [_ + __ for _ in mod for __ in mods]
                mods.extend(new_mod)
            else:
                mods = mod
        if mods:
            mod_pep = [mod_processor.add_mod(pep, one_mod) for one_mod in mods]
        else:
            mod_pep = [pep]
    else:
        mod_pep = [pep]
    return mod_pep


def add_target_charge(modpep, charge=(2, 3)):
    """
    :param modpep: the list of modified peps
    :param charge: a tuple or an integer of targeted charge state
    """
    if isinstance(charge, int):
        charge = (charge,)
    prec_list = []
    for c in charge:
        _prec = rk.assemble_prec(modpep, c)
        prec_list.append(_prec)
    return prec_list
