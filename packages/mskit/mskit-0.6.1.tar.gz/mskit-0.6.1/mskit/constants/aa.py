def element_aa2res(aa_comp: dict) -> dict:
    res_comp = aa_comp.copy()
    res_comp["H"] -= 2
    res_comp["O"] -= 1
    return res_comp


class AAComp:
    AAElement = {
        "A": {"C": 3, "N": 1, "O": 2, "H": 7},
        "R": {"C": 6, "N": 4, "O": 2, "H": 14},
        "N": {"C": 4, "N": 2, "O": 3, "H": 8},
        "D": {"C": 4, "N": 1, "O": 4, "H": 7},
        "C": {"C": 3, "N": 1, "O": 2, "H": 7, "S": 1},
        "C+": {"C": 5, "N": 2, "O": 3, "H": 10, "S": 1},
        "Q": {"C": 5, "N": 2, "O": 3, "H": 10},
        "E": {"C": 5, "N": 1, "O": 4, "H": 9},
        "G": {"C": 2, "N": 1, "O": 2, "H": 5},
        "H": {"C": 6, "N": 3, "O": 2, "H": 9},
        "I": {
            "C": 6,
            "N": 1,
            "O": 2,
            "H": 13,
        },
        "L": {
            "C": 6,
            "N": 1,
            "O": 2,
            "H": 13,
        },
        "K": {
            "C": 6,
            "N": 2,
            "O": 2,
            "H": 14,
        },
        "M": {"C": 5, "N": 1, "O": 2, "H": 11, "S": 1},
        "F": {
            "C": 9,
            "N": 1,
            "O": 2,
            "H": 11,
        },
        "P": {"C": 5, "N": 1, "O": 2, "H": 9},
        "S": {"C": 3, "N": 1, "O": 3, "H": 7},
        "T": {"C": 4, "N": 1, "O": 3, "H": 9},
        "W": {"C": 11, "N": 2, "O": 2, "H": 12},
        "Y": {"C": 9, "N": 1, "O": 3, "H": 11},
        "V": {"C": 5, "N": 1, "O": 2, "H": 11},
    }


class ResComp:
    ResElement = {aa: element_aa2res(aa_comp=aa_comp) for aa, aa_comp in AAComp.AAElement.items()}


class AA:
    AA_3to1 = {
        "Ala": "A",
        "Cys": "C",
        "Asp": "D",
        "Glu": "E",
        "Phe": "F",
        "Gly": "G",
        "His": "H",
        "Ile": "I",
        "Lys": "K",
        "Leu": "L",
        "Met": "M",
        "Asn": "N",
        "Pro": "P",
        "Gln": "Q",
        "Arg": "R",
        "Ser": "S",
        "Thr": "T",
        "Val": "V",
        "Trp": "W",
        "Tyr": "Y",
    }
    AA_1to3 = {v: k for k, v in AA_3to1.items()}
    AAList_20 = ["A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y"]

    # May have same one letter abbr
    ExtendedAA_3to1 = {
        "ALA": "A",
        "ASX": "B",
        "CYS": "C",
        "ASP": "D",
        "GLU": "E",
        "PHE": "F",
        "GLY": "G",
        "HIS": "H",
        "ILE": "I",
        "LYS": "K",
        "LEU": "L",
        "Xle": "L",
        "MET": "M",
        "ASN": "N",
        "PYL": "O",
        "PRO": "P",
        "GLN": "Q",
        "ARG": "R",
        "SER": "S",
        "THR": "T",
        "SEC": "U",
        "VAL": "V",
        "TRP": "W",
        "XAA": "X",
        "TYR": "Y",
        "GLX": "Z",
        "OTHER": "X",
        "TERM": "*",
    }

    Hydro = ["A", "F", "I", "L", "M", "P", "V", "W"]


class AAInfo:
    AAName = """\
Full name	Chinese	3-letter	1-letter
Alanine	丙氨酸	Ala	A
Cysteine	半胱氨酸	Cys	C
Asparticacid	天冬氨酸	Asp	D
Glutamicacid	谷氨酸	Glu	E
Phenylalanine	苯丙氨酸	Phe	F
Glycine	甘氨酸	Gly	G
Histidine	组氨酸	His	H
Isoleucine	异亮氨酸	Ile	I
Lysine	赖氨酸	Lys	K
Leucine	亮氨酸	Leu	L
Methionine	甲硫氨酸	Met	M
Asparagine	天冬酰胺	Asn	N
Proline	脯氨酸	Pro	P
Glutamine	谷氨酰胺	Gln	Q
Arginine	精氨酸	Arg	R
Serine	丝氨酸	Ser	S
Threonine	苏氨酸	Thr	T
Valine	缬氨酸	Val	V
Tryptophan	色氨酸	Trp	W
Tyrosine	酪氨酸	Tyr	Y\
"""

    def get_aa_name(self):
        import io
        import pandas as pd

        return pd.read_csv(io.StringIO(self.AAName), sep="\t")
