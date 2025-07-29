import os
import re
import typing

import numpy as np

from mskit import multi_kits
from .ted import TED

__all__ = ["read_fasta", "write_fasta", "FastaFile"]


def read_fasta_re(fasta_file):
    with open(fasta_file, "r") as f:
        raw_content = f.read()
    title_seq_list = re.findall(r"(>.+?\\n)([^>]+\\n?)", raw_content)
    return {title.strip("\n"): seq.replace("\n", "") for title, seq in title_seq_list}


def read_fasta(
    fasta_file,
    sep: typing.Union[None, str] = "|",
    ident_idx: int = 1,
    ident_process_func: typing.Union[None, typing.Callable] = None,
    open_mode: str = "r",
    encoding: str = "utf-8",
    skip_row: int = None,
    ignore_blank: bool = False,
) -> dict:
    """
    Use `sep=None` to skip parsing title
    print(isinstance(f, io.IOBase))
    print(isinstance(f, io.TextIOBase))
    print(isinstance(f, io.TextIOWrapper))
    """
    fasta_dict = dict()
    seq_list = []
    with open(
        fasta_file,
        open_mode,
    ) as f:
        if isinstance(skip_row, int):
            [f.readline() for _ in range(skip_row)]
        for row in f:
            if open_mode == "rb":
                row = row.decode(encoding)
            if row.startswith(">"):
                if seq_list:
                    fasta_dict[acc] = "".join(seq_list)

                if ident_process_func is not None:
                    acc = ident_process_func(row)
                else:
                    if sep is None:
                        acc = row.strip("\n")
                    else:
                        acc = row.strip("\n").split(sep)[ident_idx]

                seq_list = []
            elif not row or row == "\n":
                if ignore_blank:
                    continue
                else:
                    raise ValueError(
                        "Blank line in target FASTA file. "
                        "Check completeness of FASTA file, or use `ignore_blank=True` to ignore this error."
                    )
            else:
                seq_list.append(row.strip("\n"))
        if seq_list:
            fasta_dict[acc] = "".join(seq_list)
    return fasta_dict


seq_dict_from_fasta = read_fasta


def write_fasta(fasta: dict[str, str], file_path: str, seq_line_max_char: int = -1):
    """
    line_max_char:
        -1: Write one seq to one line
        80: Write one seq to multilines to keep the numebr of char in one line == 80
        other integer: Keep number of char equal to the customed number
    """
    if not isinstance(seq_line_max_char, int):
        raise ValueError(f"`seq_line_max_char` receives a positive integer or `-1`. Now {seq_line_max_char}")
    with open(file_path, "w", encoding="utf-8") as f:
        for title, seq in fasta.items():
            if title.startswith(">"):
                f.write(title + "\n")
            else:
                f.write(f">{title}" + "\n")

            if seq_line_max_char == -1:
                f.write(seq + "\n")
            elif isinstance(seq_line_max_char, int) and (seq_line_max_char > 0):
                f.write(
                    "".join(
                        [
                            seq[_ * seq_line_max_char : (_ + 1) * seq_line_max_char] + "\n"
                            for _ in range(int(np.ceil(len(seq) / seq_line_max_char)))
                        ]
                    )
                )


class FastaFile(object):
    """
    TODO 传入path，或content，或handle，增加skiprow和commend ident
    TODO 两个 fasta parser 合并
    """

    def __init__(
        self,
        fasta_file_path,
        open_mode="r",
        title_parse_rule: typing.Union[str, typing.Callable] = "uniprot",
        preprocess=True,
        nothing_when_init=False,
    ):
        """
        :param fasta_file_path:
        :param title_parse_rule: 'uniprot' will get the second string for title split by '|', and others will be the first string split by get_one_prefix_result blank,
        while maybe other formats of fasta title is needed later


        FASTAs = dict()
        EntryToSpecies = dict()
        SpeciesToDigestedPepSeqs = dict()
        DigestedPepToEntries = defaultdict(list)

        """

        self.fasta_file_path = fasta_file_path
        self.raw_entry_seq_map = dict()
        self.title_parse_rule = title_parse_rule

        self.id_parse_func = None
        self.comment_parse_func = None

        self.prot_acc_dict = dict()

        self._protein_info = dict()  # The description information of each protein in the fasta file
        self._protein_to_seq = dict()  # The whole sequence of each protein (No digestion)
        self._seq_to_protein = dict()  # Digested peptide to protein. The protein may be str if one else list.
        self._seq_list = []  # Digested peptides of all protein sequence in the fasta file

        if preprocess:
            self.load_fasta()

    def get_fasta_file_path(self):
        return self.fasta_file_path

    def set_fasta_file_path(self, fasta_file_path):
        if os.path.exists(fasta_file_path):
            self.fasta_file_path = os.path.abspath(fasta_file_path)
        else:
            print("Incorrect FASTA file path")
            raise FileNotFoundError(f"The FASTA file is not existed: {fasta_file_path}")

    fasta_file_path = property(get_fasta_file_path, set_fasta_file_path, doc="""""")

    def load_fasta(self, open_mode="r", method="re"):
        if method == "re":
            self.raw_entry_seq_map = read_fasta_re(self.fasta_file_path)
        else:
            self.raw_entry_seq_map = read_fasta(
                self.fasta_file_path,
                sep=None,
                ident_idx=-1,
                ident_process_func=None,
                open_mode=open_mode,
                skip_row=None,
                ignore_blank=False,
            )

    def get_title_parse_rule(self):
        return self.title_parse_rule

    def set_title_parse_rule(self, parse_rule=None, id_parse_func=None, comment_parse_func=None):
        print("enter set parse func")
        id_parse_rules = {"uniprot": lambda x: re.findall(r"^>(.+?)\|(.+?)\|(.+?)$", x)}
        comment_parse_rules = {"uniprot": lambda x: None}
        if isinstance(parse_rule, str):
            try:
                self.id_parse_func = id_parse_rules[parse_rule.lower()]  # TODO 设置一个 parse rule dict
            except KeyError:
                raise KeyError(f"Not {parse_rule} Found in The Predefined rule list")
        else:
            pass
        self.title_parse_rule = parse_rule

        if id_parse_func:
            self.id_parse_func = id_parse_func
        if comment_parse_func:
            self.comment_parse_func = comment_parse_func

    title_parse_rule = property(get_title_parse_rule, set_title_parse_rule, doc="""""")

    def __call__(self, *args, **kwargs):
        pass

    def __iter__(self):
        return iter(self.raw_entry_seq_map.items())

    def __getitem__(self, item):
        return self.prot_acc_dict[item]

    def __setitem__(self, key, value):
        self.raw_entry_seq_map[key] = value

    def __add__(self, other):  # 只保留唯一 title
        pass

    def get_all_title(self):
        pass

    def add_new_seqs(self, new_seq_dict, id_conflict=None):
        """
        id_conflict:
            new: Keep new protein seq
            origin: Keep original protein seq
            go_on: Add as PROTEIN-2
            consistent: Add as PROTEIN-2 and rename the original key to PROTEIN-1
        """
        self.raw_entry_seq_map.update(new_seq_dict)

    def to_file(self, file_path, seq_line=None):
        """
        seq_line:
            None: Write one seq to one line
            80: Write one seq to multilines to keep the numebr of char in one line == 80
            other integer: Keep number of char equal to the customed number
        """
        with open(file_path, "w") as f:
            if seq_line:
                for title, seq in self.raw_entry_seq_map.items():
                    f.write(title + "\n")
                    f.write(
                        "".join(
                            [
                                seq[_ * seq_line : (_ + 1) * seq_line] + "\n"
                                for _ in range(int(np.ceil(len(seq) / seq_line)))
                            ]
                        )
                    )
            else:
                for title, seq in self.raw_entry_seq_map:
                    f.write(title + "\n")
                    f.write(seq + "\n")

    save = to_file

    def one_protein_generator(self):
        """
        Generate title and sequence of each protein in fasta file
        """
        seq_title = ""
        seq_list = []
        with open(self.fasta_path, "r") as fasta_handle:
            for _line in fasta_handle:
                if not _line:
                    print("Blank line existed in fasta file")  # TODO 记录 blank line 的行号
                    continue
                if _line.startswith(">"):
                    if seq_title and seq_list:
                        yield seq_title, "".join(seq_list)
                    seq_title = _line.strip("\n")
                    seq_list = []
                else:
                    seq_list.append(_line.strip("\n"))
            if seq_title and seq_list:
                yield seq_title, "".join(seq_list)

    def protein2seq(self, protein_info=False):
        if not self._protein_to_seq:
            for _title, _seq in self.one_protein_generator():
                protein_ident = multi_kits.fasta_title(_title, self.title_parse_rule)
                self._protein_to_seq[protein_ident] = _seq
                if protein_info:
                    self._protein_info[protein_ident] = _title
        return self._protein_to_seq

    def seq2protein(self, miss_cleavage=(0, 1, 2), min_len=7, max_len=33) -> dict:
        if not self._seq_to_protein:
            if not self._protein_to_seq:
                self.protein2seq()

            ted = TED(
                miss_cleavage=miss_cleavage, min_len=min_len, max_len=max_len, enzyme="Trypsin", return_position="seq"
            )
            for protein_acc, seq in self._protein_to_seq.items():
                compliant_seq = ted(seq)
                for _each_seq in compliant_seq:
                    self._seq_list.append(_each_seq)
                    if _each_seq not in self._seq_to_protein:
                        self._seq_to_protein[_each_seq] = protein_acc
                    else:
                        if isinstance(self._seq_to_protein[_each_seq], str):
                            self._seq_to_protein[_each_seq] = [self._seq_to_protein[_each_seq], protein_acc]
                        elif isinstance(self._seq_to_protein[_each_seq], list):
                            self._seq_to_protein[_each_seq].append(protein_acc)
        return self._seq_to_protein

    def get_total_seqlist(self, miss_cleavage=(0, 1, 2), min_len=7, max_len=33):
        if not self._seq_list:
            self.seq2protein(miss_cleavage=miss_cleavage, min_len=min_len, max_len=max_len)
        self._seq_list = multi_kits.drop_list_duplicates(self._seq_list)
        return self._seq_list

    def merge(self):
        pass


def merge_fasta(
    *fasta: typing.Union[FastaFile, dict],
    duplicated_title: str = "keep_first",
    duplicated_seq: str = "keep_all",
):
    """
    Merge input FASTAs to one.
    :param fasta:
        Receives multi input FASTAs for `FastaFile` object or dict
        If inputs are all `FastaFile` object, this function will return
        the first `FastaFile` object (same id) with combined `protein: seq` pairs
        If any one input is `dict`, this function will return a dict with combined `protein: seq` pairs
    :param duplicated_title: one of "keep_first", "drop_all", "continous_anno"
    :param duplicated_seq: one of "keep_all", "drop_all". This will be checked after title checking


    merged_fasta = dict()
    for name, path in PATH_Fastas.items():
        fa = read_fasta(path, sep=None)
        merged_fasta.update(fa)
        print(f'Entries of {name}: {len(fa)}')
        print(f'Cumulative entries: {len(merged_fasta)}')
    """
    pass


class FastaWriter(object):
    def __init__(self, path):
        # TODO Check defined path
        self.fasta_path = path
        self.fasta_file_stream = None

    def __enter__(self):
        self.fasta_file_stream = open(self.fasta_path, "r")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fasta_file_stream.close()


class _FastaParser(
    FastaFile,
):
    def __init__(self, fasta_type="protein"):
        if fasta_type.lower() == "protein":
            super(FastaFile, self).__init__()
        elif fasta_type.lower() == "base" or fasta_type.lower() == "nucleic acid":
            pass
