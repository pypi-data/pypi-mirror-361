IntMod2General = {}


def unimod_modpep_to_intseq(x):
    if "(UniMod:1)" in x:
        x = x.replace("(UniMod:1)", "")
        x = "*" + x
    else:
        x = "@" + x
    x = x.replace(".", "")
    x = x.replace("C(UniMod:4)", "C")
    x = x.replace("M(UniMod:35)", "1")
    x = x.replace("S(UniMod:21)", "2")
    x = x.replace("T(UniMod:21)", "3")
    x = x.replace("Y(UniMod:21)", "4")
    return x


def intseq_to_unimod_modpep(x):
    if x[0] == "*":
        x = "(UniMod:1)" + x[1:]
    elif x[0] == "@":
        x = x[1:]
    else:
        pass
    x = x.replace("C", "C(UniMod:4)")
    x = x.replace("1", "M(UniMod:35)")
    x = x.replace("2", "S(UniMod:21)")
    x = x.replace("3", "T(UniMod:21)")
    x = x.replace("4", "Y(UniMod:21)")
    return x


def sn_modpep_to_intseq(x):
    x = x.replace("_", "")
    if "[Acetyl (Protein N-term)]" in x:
        x = x.replace("[Acetyl (Protein N-term)]", "")
        x = "*" + x
    else:
        x = "@" + x
    x = x.replace("C[Carbamidomethyl (C)]", "C")
    x = x.replace("M[Oxidation (M)]", "1")
    x = x.replace("S[Phospho (STY)]", "2")
    x = x.replace("T[Phospho (STY)]", "3")
    x = x.replace("Y[Phospho (STY)]", "4")
    return x


def intseq_to_sn_modpep(x):
    if x[0] == "*":
        x = "[Acetyl (Protein N-term)]" + x[1:]
    elif x[0] == "@":
        x = x[1:]
    else:
        pass
    x = x.replace("C", "C[Carbamidomethyl (C)]")
    x = x.replace("1", "M[Oxidation (M)]")
    x = x.replace("2", "S[Phospho (STY)]")
    x = x.replace("3", "T[Phospho (STY)]")
    x = x.replace("4", "Y[Phospho (STY)]")
    x = f"_{x}_"
    return x


def mq_modpep_to_intseq_1_6(x):
    x = x.replace("_", "")
    if "(Acetyl (Protein N-term))" in x:
        x = x.replace("(Acetyl (Protein N-term))", "")
        x = f"*{x}"
    else:
        x = f"@{x}"
    x = x.replace("C(Carbamidomethyl (C))", "C")
    x = x.replace("M(Oxidation (M))", "1")
    x = x.replace("S(Phospho (STY))", "2")
    x = x.replace("T(Phospho (STY))", "3")
    x = x.replace("Y(Phospho (STY))", "4")
    return x


def mq_modpep_to_intseq_1_5(x):
    x = x.replace("_", "")
    if "(ac)" in x:
        x = x.replace("(ac)", "")
        x = f"*{x}"
    else:
        x = f"@{x}"
    x = x.replace("C(Carbamidomethyl (C))", "C")
    x = x.replace("M(ox)", "1")
    x = x.replace("S(ph)", "2")
    x = x.replace("T(ph)", "3")
    x = x.replace("Y(ph)", "4")
    return x


def comet_to_intseq(x):
    """
    Comet style (modifications with symbols annotated):
        S@/T@/Y@ for Phospho (STY)
        M* for Oxidation (M)
        n# for Acetyl (N-term)
        Example: n#DFM*SPKFS@LT@DVEY@PAWCQDDEVPITM*QEIR
    """
    x = x.replace("_", "")

    x = x.replace("M*", "1")
    x = x.replace("S@", "2")
    x = x.replace("T@", "3")
    x = x.replace("Y@", "4")

    if "n#" in x:
        x = x.replace("n#", "")
        x = "*" + x
    else:
        x = "@" + x

    return x
