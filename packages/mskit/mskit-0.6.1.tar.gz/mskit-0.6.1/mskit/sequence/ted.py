import re
from typing import Union

import numpy as np

from mskit import multi_kits as rk
from mskit.constants.enzyme import Enzyme

__all__ = [
    "find_cleavage_sites_by_re",
    "find_cleavage_sites_by_explicit_defination",
    "find_cleavage_sites",
    "TED",
]


def find_cleavage_sites_by_re():
    pass


def find_cleavage_sites_by_explicit_defination():
    pass


def find_cleavage_sites():
    pass


def count_mc(pep: str, cleav_site=None):
    return len(re.findall("[KR](?<!$)", pep))


class TED(object):
    def __init__(
        self,
        miss_cleavage=(0, 1, 2),
        min_len=7,
        max_len=33,
        enzyme="Trypsin/P",
        toggle_nterm_m=True,
        return_type="seq",
        extend_n=False,
    ):
        """
        Theoretical Enzyme Digestion -> TED

        :param miss_cleavage: int or tuple
            This can be int or tuple, while it will be converted into tuple when use
        :param min_len:
        :param max_len:
        :param enzyme:
            Enzyme name or a regular expression to define the digestion rules. Currently supported enzymes are Trypsin, Trypsin/P, lysC, and LysC/P
        :param toggle_nterm_m:
            If 'M' on sequence N-terminal, remove this M and go continue (2), or both remove and keep this M and go continue (1 or True), or nothing to do (0 or False)
        :param return_type:
            'seq' or 'site_seq'
        :param extend_n: False or None or int.
            Nothing to do with the default False, and the n AAs before and after the seq will be returned if int assigned

        TODO exclude some unusual aa if param assigned
        """
        self._enzyme = Enzyme()
        self._mc = self._parse_mc(miss_cleavage)
        # TODO Add property for length (min len 7 for default and the func will be able to parse both tuple or int)
        self._min_len = min_len
        self._max_len = max_len
        self._enzyme_names, self._enzyme_rules = self._parse_enzyme(enzyme)
        self._toggle_nterm_m = toggle_nterm_m
        self._cleavage_nterm_m, self._need_optional_nterm_m = self._parse_toggle_nterm_m(toggle_nterm_m)
        self._return_type = self._parse_return_type(return_type)
        self._extend_n = self._parse_extend_n(extend_n)

    @staticmethod
    def _parse_mc(mc):
        if isinstance(mc, (tuple, list)):
            pass
        elif isinstance(mc, int):
            mc = (mc,)
        else:
            try:
                mc = (int(mc),)
            except TypeError:
                raise TypeError("Miss cleavage shoule be int or tuple of int")
        return mc

    def get_mc(self):
        return self._mc

    def set_mc(self, mc):
        self._mc = self._parse_mc(mc)

    mc = property(get_mc, set_mc, doc="""Miss cleavage for enzyme digestion""")

    def __find_enzyme(self, enzyme, enzyme_names, enzyme_rules):
        if isinstance(enzyme, str):
            if enzyme not in self._enzyme.AllEnzymes:
                print(
                    f"The input enzyme has no pre-defined digestion rule, the enzyme now used is: {enzyme}.\n"
                    f"This input will be regarded as a regular expression."
                )
                enzyme_rules.append(enzyme)
            else:
                enzyme_names.append(enzyme)
                enzyme_rules.append(self._enzyme.Enzymes[enzyme]["RE"])
        else:
            raise ValueError(f"The input enzyme {enzyme} is not a string")
        return enzyme_names, enzyme_rules

    def _parse_enzyme(self, enzyme):
        enzyme_names = []
        enzyme_rules = []
        if isinstance(enzyme, str):
            enzyme = (enzyme,)
        elif isinstance(enzyme, (list, tuple, set)):
            pass
        else:
            raise ValueError(f"The input enzyme can not be parsed: {enzyme}")
        for each_enzyme in enzyme:
            enzyme_names, enzyme_rules = self.__find_enzyme(each_enzyme, enzyme_names, enzyme_rules)
        return enzyme_names, enzyme_rules

    def get_enzyme(self):
        return self._enzyme_names, self._enzyme_rules

    def set_enzyme(self, enzyme):
        self._enzyme_names, self._enzyme_rules = self._parse_enzyme(enzyme)

    enzyme = property(get_enzyme, set_enzyme, doc="""Enzyme used for digestion""")
    # TODO enzyme -> digestion rule, change enzyme as a param
    digestion_rule = None

    @staticmethod
    def _parse_return_type(return_type: str):
        if return_type not in ["seq", "site_seq"]:
            raise TypeError(f"The input of return_type should be 'seq' or 'site_seq', now: {return_type}")
        return return_type

    def get_return_type(self):
        return self._return_type

    def set_return_type(self, return_type: str):
        self._return_type = self._parse_return_type(return_type)

    return_type = property(
        get_return_type,
        set_return_type,
        doc="""Return type can be seq or site_seq.
    If seq: A list of seq will be returned. ['ADEFHK', 'PQEDAK' , ...]
    If site_seq: A list of site and seq will be returned. [(0, 'ADEFHK'), (12, 'PQEDAK'), ...]""",
    )

    @staticmethod
    def _parse_extend_n(extend_n: Union[bool, None, int]):
        if extend_n is True:
            extend_n = 7
            print(f"The `extend_n` is set to `True` and a conventional sequence window 7 is assigned")
        elif extend_n is None:
            extend_n = False
        elif extend_n is False:
            pass
        elif isinstance(extend_n, int):
            if extend_n == 0:
                extend_n = False
            elif extend_n < 0:
                raise ValueError
            else:
                pass
        else:
            raise TypeError(
                f"The input of extend_n should be False or None or int, now: {extend_n} with a type {type(extend_n)}"
            )
        return extend_n

    def get_extend_n(self):
        return self._extend_n

    def set_extend_n(self, extend_n: Union[bool, None, int]):
        self._extend_n = self._parse_extend_n(extend_n)

    extend_n = property(
        get_extend_n,
        set_extend_n,
        doc="""Extended AA number can be False or None or int.
    Nothing to do with the default False or None is assigned.
    If int: the n AAs before and after the seq will be returned.
    If True: the n will be set to 7 as a conventional sequence window""",
    )

    @staticmethod
    def _parse_toggle_nterm_m(toggle_nterm_m):
        if toggle_nterm_m == 2:
            cleavage_nterm_m = True
            need_optional_nterm_m = False
        elif toggle_nterm_m == 1 or toggle_nterm_m is True:
            cleavage_nterm_m = True
            need_optional_nterm_m = True
        elif toggle_nterm_m == 0 or toggle_nterm_m is False:
            cleavage_nterm_m = False
            need_optional_nterm_m = False
        else:
            raise ValueError("The input of `toggle_nterm_m` should be a value of `[2, 1, True, 0, False]`")
        return cleavage_nterm_m, need_optional_nterm_m

    def get_toggle_nterm_m(self):
        return self._toggle_nterm_m

    def set_toggle_nterm_m(self, toggle_nterm_m: Union[bool, int]):
        self._cleavage_nterm_m, self._need_optional_nterm_m = self._parse_toggle_nterm_m(toggle_nterm_m)

    toggle_nterm_m = property(
        get_toggle_nterm_m,
        set_toggle_nterm_m,
        doc="""If "M" is on sequence N-terminal, 
set this param to `2` to remove this M and do digestion, 
set this param to `1` or `True` to both remove and keep this M and do digestion, 
set this param to `0` or `False` to do nothing on this "M" and do digestion""",
    )

    #     def __str__(self):
    #         self.__dict__
    #         msg = '''\
    # Theoretical Enzyme Digestion
    #
    #         '''
    #         print('')

    def cleavage(self, seq, add_info=None):
        seq = seq.replace("\n", "").replace(" ", "")
        seq_len = len(seq)

        cleavage_pos = rk.sum_list([[_.end() for _ in re.finditer(rule, seq)] for rule in self._enzyme_rules])
        if seq[0] == "M" and self._cleavage_nterm_m:
            cleavage_pos += [1, seq_len]
        else:
            cleavage_pos += [0, seq_len]
        cleavage_pos = np.array(sorted(set(cleavage_pos)))
        cleavage_pos_num = len(cleavage_pos)

        pos_comb = []
        for mc in self._mc:
            idxs = np.arange(cleavage_pos_num)
            _keep_idx_num = cleavage_pos_num - mc - 1
            start_idxs = cleavage_pos[idxs[:_keep_idx_num]]
            end_poss = cleavage_pos[np.roll(idxs, -(mc + 1))[:_keep_idx_num]]

            if seq[0] == "M" and self._need_optional_nterm_m and (len(end_poss) != 0):
                pos_comb.append([0, end_poss[0]])
            pos_comb.extend(np.stack((start_idxs, end_poss), axis=0).T.tolist())

        compliant_seq = []
        for start_idx, end_pos in pos_comb:
            one_seq = seq[start_idx:end_pos]
            seq_len = len(one_seq)
            if seq_len < self._min_len or seq_len > self._max_len:
                continue
            else:
                if self._return_type == "seq":
                    one_data = (one_seq,)
                elif self._return_type == "site_seq":
                    one_data = (start_idx, one_seq)
                else:
                    raise ValueError
                if self._extend_n:
                    if start_idx < self._extend_n:
                        prev_seq = "_" * (self._extend_n - start_idx) + seq[:start_idx]
                    else:
                        prev_seq = seq[start_idx - self._extend_n : start_idx]
                    back_seq = seq[end_pos : end_pos + self._extend_n]
                    if len(back_seq) < self._extend_n:
                        back_seq = back_seq + "_" * (self._extend_n - len(back_seq))
                    one_data = (*one_data, prev_seq, back_seq)
                if add_info is not None:
                    if not isinstance(add_info, (tuple, list)):
                        add_info = (add_info,)
                    one_data = (*one_data, *add_info)
                if len(one_data) == 1:
                    one_data = one_data[0]
                compliant_seq.append(one_data)
        return compliant_seq

    def __call__(self, seq, add_info=None):
        return self.cleavage(seq, add_info=add_info)
