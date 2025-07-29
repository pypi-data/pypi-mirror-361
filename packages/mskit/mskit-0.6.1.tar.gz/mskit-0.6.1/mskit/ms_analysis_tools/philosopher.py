import typing
from mskit import multi_kits as rk

Philosopher_OutputDtype_Protein = {
    "Protein": "str",
    "Protein ID": "str",
    "Entry Name": "str",
    "Gene": "object",
    "Length": "int32",
    "Organism": "object",
    "Protein Description": "str",
    "Protein Existence": "object",
    "Protein Probability": "float64",
    "Top Peptide Probability": "float64",
    "Total Peptides": "int32",
    "Unique Peptides": "int32",
    "Razor Peptides": "int32",
    "Total Spectral Count": "int64",
    "Unique Spectral Count": "int64",
    "Razor Spectral Count": "int64",
    "Total Intensity": "float64",
    "Unique Intensity": "float64",
    "Razor Intensity": "float64",
    "Razor Assigned Modifications": "object",
    "Razor Observed Modifications": "object",
    "Indistinguishable Proteins": "object",
}

Philosopher_OutputDtype_Peptide = {
    "Peptide": "str",
    "Prev AA": "str",
    "Next AA": "str",
    "Peptide Length": "int16",
    "Charges": "str",  # int if only one charge state occurred on this peptide, while str like '2, 3' when multi charge states were identified
    "Probability": "float64",
    "Spectral Count": "int64",
    "Intensity": "float64",
    "Assigned Modifications": "object",
    "Observed Modifications": "object",
    "Protein": "str",
    "Protein ID": "str",
    "Entry Name": "str",
    "Gene": "object",
    "Protein Description": "str",
    "Mapped Genes": "object",
    "Mapped Proteins": "object",
}

Philosopher_OutputDtype_Ion = {
    # Protein / Gene
    "Protein": "str",
    "Protein ID": "str",
    "Entry Name": "str",
    "Gene": "object",
    "Protein Description": "str",
    "Mapped Genes": "object",
    "Mapped Proteins": "object",
    # Peptide
    "Peptide Sequence": "str",
    "Modified Sequence": "str",
    "Prev AA": "str",  # AA or - for blank
    "Next AA": "str",
    "Peptide Length": "int16",
    "M/Z": "float64",
    "Charge": "int8",
    "Observed Mass": "float64",
    "Assigned Modifications": "object",
    "Observed Modifications": "object",
    # Scores
    "Probability": "float64",
    "Expectation": "float64",
    # Quant
    "Spectral Count": "int32",
    "Intensity": "float64",
}

Philosopher_OutputDtype_PSM = {
    "Spectrum": "str",
    "Spectrum File": "str",
    "Peptide": "str",
    "Modified Peptide": "object",
    "Prev AA": "str",
    "Next AA": "str",
    "Peptide Length": "int16",
    "Charge": "int8",
    "Retention": "float64",  # in seconds
    "Observed Mass": "float64",
    "Calibrated Observed Mass": "float64",
    "Observed M/Z": "float64",
    "Calibrated Observed M/Z": "float64",
    "Calculated Peptide Mass": "float64",
    "Calculated M/Z": "float64",
    "Delta Mass": "float64",
    "Expectation": "float64",
    "Hyperscore": "float64",
    "Nextscore": "float64",
    "PeptideProphet Probability": "float64",
    "Number of Enzymatic Termini": "int8",
    "Number of Missed Cleavages": "int8",
    "Protein Start": "int16",
    "Protein End": "int16",
    "Intensity": "float64",
    "Assigned Modifications": "object",
    "Observed Modifications": "object",
    "Is Unique": "bool",
    "Protein": "str",
    "Protein ID": "str",
    "Entry Name": "str",
    "Gene": "object",
    "Protein Description": "str",
    "Mapped Genes": "object",
    "Mapped Proteins": "object",
}


def get_ptmprophet_added_psm_cols(added_varmod_mass: typing.Union[list, tuple]):
    return Philosopher_OutputDtype_PSM | rk.union_dicts(
        *[{m: "object", f"{m} Best Localization": "float64"} for m in added_varmod_mass]
    )
