""" """

import pkg_resources

unimod = pkg_resources.resource_filename("mskit", "package_data/unimod.xml")


class ModificationElementComposition:
    ModToElementComp = {
        "Acetyl": {"C": 2, "O": 1, "H": 2},
        "Acetylation": {"C": 2, "O": 1, "H": 2},
        "UniMod:1": {"C": 2, "O": 1, "H": 2},
        "Carbamidomethyl": {"C": 2, "N": 1, "O": 1, "H": 3},
        "UniMod:4": {"C": 2, "N": 1, "O": 1, "H": 3},
        "Phospho": {"H": 1, "P": 1, "O": 3},
        "UniMod:21": {"H": 1, "P": 1, "O": 3},
        "Oxidation": {"O": 1},
        "UniMod:35": {"O": 1},
        "Deamidation": {"O": 1, "N": -1, "H": -1},
        "UniMod:7": {"O": 1, "N": -1, "H": -1},
        "Methyl": {"C": 1, "H": 2},
        "UniMod:34": {"C": 1, "H": 2},
        "Dimethyl": {"C": 2, "H": 4},
        "UniMod:36": {"C": 2, "H": 4},
        "Trimethyl": {"C": 3, "H": 6},
        "UniMod:37": {"C": 3, "H": 6},
        "Formyl": {"C": 1, "O": 1},
        "UniMod:122": {"C": 1, "O": 1},
        "Crotonyl": {"C": 4, "O": 1, "H": 4},
        "UniMod:1363": {"C": 4, "O": 1, "H": 4},
        "Nitro": {"O": 2, "N": 1, "H": -1},
        "UniMod:354": {"O": 2, "N": 1, "H": -1},
        "Malonyl": {"C": 3, "O": 3, "H": 2},
        "UniMod:747": {"C": 3, "O": 3, "H": 2},
    }

    NeutralLoss = {"H2O": {"H": 2, "O": 1}}


class BasicModification:
    # Pre-defined mods, where key means query mod and value is used for assembling queried mod
    StandardMods = {
        "Carbamidomethyl": "Carbamidomethyl",
        "Oxidation": "Oxidation",
        "Phospho": "Phospho",
        "Acetyl": "Acetyl",
    }

    # To extend the query space. Each mod has its alias and itself for quering
    __ModAliasList = {
        "Carbamidomethyl": ["Carbamidomethyl", "Carbamid", "Carb", "Carbamidomethyl[C]"],
        "Oxidation": ["Oxidation", "Oxi", "Ox", "Oxidation[M]"],
        "Phospho": [
            "Phospholation",
            "Phospho",
            "Phos",
        ],
        "Acetyl": ["_[Acetyl (Protein N-term)]"],
    }
    ModAliasDict = {}
    for standard, aliases in __ModAliasList.items():
        for alias in aliases:
            ModAliasDict[alias] = standard
    for alias in list(ModAliasDict.keys()):
        ModAliasDict[alias.upper()] = ModAliasDict[alias]
        ModAliasDict[alias.lower()] = ModAliasDict[alias]

    # Mod rule. This defines the method for mod assembly
    StandardModRule = r"[{mod} ({aa})]"
    ModRuleDict = {
        "standard": StandardModRule,
    }

    ModAA = {
        "Carbamidomethyl": ["C"],
        "Oxidation": ["M"],
        "Phospho": ["S", "T", "Y"],
    }

    ExtendModAA = ModAA.copy()
    ExtendModAA["Phospho"].extend(["H", "R", "K", "D", "G", "M", "V", "P", "N", "A"])
