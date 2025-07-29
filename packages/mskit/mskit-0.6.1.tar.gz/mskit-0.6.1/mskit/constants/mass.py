""" """


class ElementMass:
    Mono = {
        "C": 12.0,
        "H": 1.0078250321,
        "2H": 2.014102,
        "O": 15.9949146221,
        "N": 14.0030740052,
        "P": 30.97376151,
        "S": 31.97207069,
        "Na": 22.98976967,
        "Cl": 34.96885271,
        "Ca": 39.9625912,
        "Fe": 55.9349421,
        "Cu": 62.9296011,
    }

    Aver = {}


class CompoundMass:
    CompoundMass = {
        "H2O": ElementMass.Mono["H"] * 2 + ElementMass.Mono["O"],
        "NH3": ElementMass.Mono["N"] + ElementMass.Mono["H"] * 3,
        "H3PO4": ElementMass.Mono["H"] * 3 + ElementMass.Mono["P"] + ElementMass.Mono["O"] * 4,
        "HPO3": ElementMass.Mono["H"] + ElementMass.Mono["P"] + ElementMass.Mono["O"] * 3,
        "C2H2O": ElementMass.Mono["C"] * 2 + ElementMass.Mono["H"] * 2 + ElementMass.Mono["O"],
        "CH2": ElementMass.Mono["C"] + ElementMass.Mono["H"] * 2,
        "CO": ElementMass.Mono["C"] + ElementMass.Mono["O"],
        "C3H6": ElementMass.Mono["C"] * 3 + ElementMass.Mono["H"] * 6,
    }


class Mass:
    ResMass = {
        "A": 71.0371138,
        "C": 103.00918,
        "C+": 160.0306481,
        "D": 115.0269429,
        "E": 129.042593,
        "F": 147.0684139,
        "G": 57.0214637,
        "H": 137.0589118,
        "I": 113.0840639,
        "K": 128.094963,
        "L": 113.0840639,
        "M": 131.0404846,
        "N": 114.0429274,
        "P": 97.0527638,
        "Q": 128.0585774,
        "R": 156.101111,
        "S": 87.0320284,
        "T": 101.0476784,
        "V": 99.0684139,
        "W": 186.0793129,
        "Y": 163.0633285,
    }

    ProtonMass = 1.0072766  # H+
    NeutronMass = (
        1.008665  # This can not be directly added to element due to the mass difference caused by binding energy
    )
    ElectronMass = ElementMass.Mono["H"] - ProtonMass
    IsotopeMass = 1.003

    ModMass = {
        "Carbamidomethyl": 57.0214637,
        "Carbamidomethyl (C)": 57.0214637,
        "[Carbamidomethyl (C)]": 57.0214637,
        "[57]": 57.0214637,
        "[+57]": 57.0214637,
        "[car]": 57.0214637,
        "(car)": 57.0214637,
        "(ca)": 57.0214637,
        "UniMod:4": 57.0214637,
        "(UniMod:4)": 57.0214637,
        "Oxidation": ElementMass.Mono["O"],
        "Oxidation (M)": ElementMass.Mono["O"],
        "[Oxidation (M)]": ElementMass.Mono["O"],
        "[16]": ElementMass.Mono["O"],
        "[+16]": ElementMass.Mono["O"],
        "[ox]": ElementMass.Mono["O"],
        "(ox)": ElementMass.Mono["O"],
        "UniMod:35": ElementMass.Mono["O"],
        "(UniMod:35)": ElementMass.Mono["O"],
        "Phospho": CompoundMass.CompoundMass["HPO3"],
        "Phosphorylation": CompoundMass.CompoundMass["HPO3"],
        "Phospho (STY)": CompoundMass.CompoundMass["HPO3"],
        "[Phospho (STY)]": CompoundMass.CompoundMass["HPO3"],
        "[80]": CompoundMass.CompoundMass["HPO3"],
        "[+80]": CompoundMass.CompoundMass["HPO3"],
        "[ph]": CompoundMass.CompoundMass["HPO3"],
        "(ph)": CompoundMass.CompoundMass["HPO3"],
        "UniMod:21": CompoundMass.CompoundMass["HPO3"],
        "(UniMod:21)": CompoundMass.CompoundMass["HPO3"],
        "Acetyl": CompoundMass.CompoundMass["C2H2O"],
        "Acetyl (N-term)": CompoundMass.CompoundMass["C2H2O"],
        "Acetyl (prot N-term)": CompoundMass.CompoundMass["C2H2O"],
        "Acetyl (Prot N-term)": CompoundMass.CompoundMass["C2H2O"],
        "Acetyl (Protein N-term)": CompoundMass.CompoundMass["C2H2O"],
        "[Acetyl (N-term)]": CompoundMass.CompoundMass["C2H2O"],
        "[42]": CompoundMass.CompoundMass["C2H2O"],
        "[+42]": CompoundMass.CompoundMass["C2H2O"],
        "[ac]": CompoundMass.CompoundMass["C2H2O"],
        "(ac)": CompoundMass.CompoundMass["C2H2O"],
        "UniMod:1": CompoundMass.CompoundMass["C2H2O"],
        "(UniMod:1)": CompoundMass.CompoundMass["C2H2O"],
        "Methylation": CompoundMass.CompoundMass["CH2"],
        "UniMod:34": CompoundMass.CompoundMass["CH2"],
        "(UniMod:34)": CompoundMass.CompoundMass["CH2"],
        "Formylation": CompoundMass.CompoundMass["CO"],
        "UniMod:122": CompoundMass.CompoundMass["CO"],
        "(UniMod:122)": CompoundMass.CompoundMass["CO"],
        "Deamidation": 0.984016,
        "UniMod:7": 0.984016,
        "(UniMod:7)": 0.984016,
        "Trimethyl": CompoundMass.CompoundMass["C3H6"],
        "UniMod:37": CompoundMass.CompoundMass["C3H6"],
        "(UniMod:37)": CompoundMass.CompoundMass["C3H6"],
        "TMT": 229.1629,
        "1": 147.0353992,  # M[16]
        "2": 167.03203,  # S[80]
        "3": 181.04768,  # T[80]
        "4": 243.06333,  # Y[80]
    }

    ModLossMass = {
        "Noloss": 0.0,
        "H2O": CompoundMass.CompoundMass["H2O"],
        "NH3": CompoundMass.CompoundMass["NH3"],
        "H3PO4": CompoundMass.CompoundMass["H3PO4"],
    }


# C[Carbamidomethyl] = 103.00918 + 57.0214637
# M[Oxidation] = 131.04048 + 16

# H2O + H+ -> 'e'
# H+ -> 'h'
