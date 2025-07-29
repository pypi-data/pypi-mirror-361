"""
1.
This stores many different modification display methods, and all the modification will be got from here.

Shorthand:
Spectronaut -> SN

"""

import typing
import pandas as pd

from mskit import multi_kits as rk


class LossType(object):
    SN_to_Readable = {
        "noloss": "Noloss",
        "H2O": "1,H2O",
        "NH3": "1,NH3",
        "H3PO4": "1,H3PO4",
        "1(+H2+O)1(+H3+O4+P)": "1,H2O;1,H3PO4",
        "1(+H3+N)1(+H3+O4+P)": "1,NH3;1,H3PO4",
        "2(+H3+O4+P)": "2,H3PO4",
        "1(+H2+O)2(+H3+O4+P)": "1,H2O;2,H3PO4",
        "1(+H3+N)2(+H3+O4+P)": "1,NH3;2,H3PO4",
        "3(+H3+O4+P)": "3,H3PO4",
        "1(+H2+O)3(+H3+O4+P)": "1,H2O;3,H3PO4",
        "1(+H3+N)3(+H3+O4+P)": "1,NH3;3,H3PO4",
        "4(+H3+O4+P)": "4,H3PO4",
        "1(+H2+O)4(+H3+O4+P)": "1,H2O;4,H3PO4",
        "1(+H3+N)4(+H3+O4+P)": "1,NH3;4,H3PO4",
        "5(+H3+O4+P)": "5,H3PO4",
        "1(+H2+O)5(+H3+O4+P)": "1,H2O;5,H3PO4",
        "1(+H3+N)5(+H3+O4+P)": "1,NH3;5,H3PO4",
    }

    Readable_to_SN = {v: k for k, v in SN_to_Readable.items()}
    PreOrder = list(SN_to_Readable.keys())

    SN_to_Readable_v13 = SN_to_Readable.copy()
    SN_to_Readable_v13["1(+H9+N+O8+P2)"] = ("1,NH3;2,H3PO4",)  # This will occur in SN 13


class SNLibraryTitle(object):
    LibraryMainCol = [
        "PrecursorCharge",
        "ModifiedPeptide",
        "StrippedPeptide",
        "iRT",
        "LabeledPeptide",
        "PrecursorMz",
        "FragmentLossType",
        "FragmentNumber",
        "FragmentType",
        "FragmentCharge",
        "FragmentMz",
        "RelativeIntensity",
        "ProteinGroups",
    ]
    LibraryMainColPGOut = [
        "PrecursorCharge",
        "ModifiedPeptide",
        "StrippedPeptide",
        "iRT",
        "LabeledPeptide",
        "PrecursorMz",
        "FragmentLossType",
        "FragmentNumber",
        "FragmentType",
        "FragmentCharge",
        "FragmentMz",
        "RelativeIntensity",
    ]


SN_Lib_Dtype = {
    "ReferenceRun": "object",
    "PrecursorCharge": "int64",
    "Workflow": "object",
    "IntModifiedPeptide": "str",
    "CV": "float64",
    "AllowForNormalization": "bool",
    "ModifiedPeptide": "str",
    "StrippedPeptide": "str",
    "iRT": "float64",
    "IonMobility": "float64",
    "iRTSourceSpecific": "object",
    "BGSInferenceId": "object",
    "IsProteotypic": "bool",
    "IntLabeledPeptide": "str",
    "LabeledPeptide": "str",
    "PrecursorMz": "float64",
    "ReferenceRunQvalue": "float64",
    "ReferenceRunMS1Response": "float64",
    "FragmentLossType": "object",
    "FragmentNumber": "int64",
    "FragmentType": "str",
    "FragmentCharge": "int64",
    "FragmentMz": "float64",
    "RelativeIntensity": "float64",
    "ExcludeFromAssay": "bool",
    "Database": "object",
    "ProteinGroups": "object",
    "UniProtIds": "object",
    "Protein Name": "object",
    "ProteinDescription": "object",
    "Organisms": "object",
    "OrganismId": "object",
    "Genes": "object",
    "Protein Existence": "object",
    "Sequence Version": "object",
    "FASTAName": "object",
}

SN_NormalReport_Dtype = {
    "R.Condition": "object",  # may be string, int, float, nan
    "R.FileName": "str",
    "R.Fraction": "object",
    "R.Replicate": "object",  # may be int, nan
    "PG.Genes": "object",  # may be string, nan, or comb of two
    "PG.Organisms": "object",  # may be string, nan, or comb of two
    "PG.ProteinGroups": "object",
    "PG.Coverage": "object",  # may be nan or float in string like '1.1;2.2'
    "PG.Cscore": "float64",
    "PG.Cscore (Run-Wise)": "float64",
    "PG.IsSingleHit": "bool",
    "PG.Pvalue": "float64",
    "PG.PValue (Run-Wise)": "float64",
    "PG.Qvalue": "float64",
    "PG.QValue (Run-Wise)": "float64",
    "PG.RunEvidenceCount": "int64",
    "PG.IBAQ": "object",  # may be nan or float only or float in string like '1.1;2.2'
    "PG.MS1Quantity": "float64",
    "PG.Meta": "object",
    "PG.OrganismId": "object",
    "PG.WBGene": "object",
    "PG.Locus": "object",
    "PG.Status": "object",
    "PG.MS2Quantity": "float64",
    "PG.NrOfModifiedSequencesUsedForQuantification": "int64",
    "PG.Quantity": "float64",
    "PG.PEP": "float64",
    "PG.PEP (Run-Wise)": "float64",
    "PG.ProteinAccessions": "object",
    "PEP.GroupingKeyType": "object",
    "PEP.IsProteinGroupSpecific": "object",  # usually bool if fasta provided, or str as "Unknown"
    "PEP.IsProteotypic": "object",  # usually bool if fasta provided, or str as "Unknown"
    "PEP.NrOfMissedCleavages": "object",  # usually int if fasta provided, or str as "Unknown"
    "PEP.PeptidePosition": "object",
    "PEP.StrippedSequence": "object",
    "PEP.Rank": "int64",
    "PEP.RunEvidenceCount": "int64",
    "PEP.MS1Quantity": "float64",
    "PEP.MS2Quantity": "float64",
    "PEP.Quantity": "float64",
    "PEP.UsedForProteinGroupQuantity": "bool",
    "PEP.GroupingKey": "object",
    "PEP.Rank.1": "float64",
    "EG.IntModifiedPeptide": "object",
    "FG.IonMobility": "float64",  # Used in SN15
    "FG.ApexIonMobility": "float64",  # Used in SN16
    "EG.iRTPredicted": "float64",
    "EG.IsDecoy": "bool",
    "EG.ModifiedPeptide": "object",
    "EG.Identified": "bool",
    "EG.PEP": "float64",
    "EG.Pvalue": "float64",
    "EG.Qvalue": "float64",
    "EG.Svalue": "float64",
    "EG.ApexRT": "float64",
    "EG.DatapointsPerPeak": "float64",
    "EG.DeltaiRT": "float64",
    "EG.DeltaRT": "float64",
    "EG.EndiRT": "float64",
    "EG.EndRT": "float64",
    "EG.FWHM": "float64",
    "EG.FWHM (iRT)": "float64",
    "EG.iRTEmpirical": "float64",
    "EG.MeanApexRT": "float64",
    "EG.MeanTailingFactor": "float64",
    "EG.PeakWidth": "float64",
    "EG.PeakWidth (iRT)": "float64",
    "EG.RTPredicted": "float64",
    "EG.StartiRT": "float64",
    "EG.StartRT": "float64",
    "EG.SignalToNoise": "float64",
    "EG.AvgProfileQvalue": "float64",
    "EG.ConditionCV": "float64",
    "EG.GlobalCV": "float64",
    "EG.MaxProfileQvalue": "float64",
    "EG.MinProfileQvalue": "float64",
    "EG.PercentileQvalue": "float64",
    "EG.HasLocalizationInformation": "bool",
    "EG.ProteinPTMLocations": "object",
    "EG.PTMAssayCandidateScore": "float64",
    "EG.PTMAssayProbability": "float64",
    "EG.PTMLocalizationProbabilities": "str",
    "EG.IsImputed": "bool",
    "EG.NormalizationFactor": "float64",
    "EG.TargetQuantity (Settings)": "float64",
    "EG.TotalQuantity (Settings)": "float64",
    "EG.UsedForPeptideQuantity": "bool",
    "EG.UsedForProteinGroupQuantity": "bool",
    "EG.UsedInNormalizationSet": "bool",
    "EG.Cscore": "float64",
    "EG.IntCorrScore": "float64",
    "EG.Noise": "float64",
    "EG.IonMobility": "float64",
    "EG.NormalizedCscore": "float64",
    "EG.PTMPositions": "float64",
    "EG.PTMProbabilities": "float64",
    "EG.PTMSites": "float64",
    "EG.ReferenceQuantity (Settings)": "float64",
    "FG.LabeledSequence": "object",
    "FG.Charge": "int64",
    "FG.FragmentCount": "int64",
    "FG.PrecMz": "float64",
    "FG.PrecMzCalibrated": "float64",
    "FG.FWHM": "float64",
    "FG.PeakRTs (MS1)": "object",
    "FG.PeakRTs (MS2)": "object",
    "FG.PrecWindow": "object",
    "FG.PrecWindowNumber": "int64",
    "FG.PrecursorSignalToNoise": "float64",
    "FG.SignalToNoise": "float64",
    "FG.ShapeQualityScore": "float64",
    "FG.ShapeQualityScore (MS1)": "float64",
    "FG.ShapeQualityScore (MS2)": "float64",
    "FG.MS1IsotopeQuantity": "object",
    "FG.MS1Quantity": "float64",
    "FG.MS1RawQuantity": "float64",
    "FG.MS2Quantity": "float64",
    "FG.MS2RawQuantity": "float64",
    "FG.Quantity": "float64",
    "FG.CalibratedMassAccuracy (PPM)": "float64",
    "FG.CalibratedMz": "float64",
    "FG.MeasuredMz": "float64",
    "FG.Noise": "float64",
    "FG.PPMTolerance": "float64",
    "FG.RawMassAccuracy (PPM)": "float64",
    "FG.TheoreticalMz": "float64",
    "FG.Tolerance": "float64",
}


def get_sn_report_ptms(
    file_or_df,
    ptm_col_prefix: typing.Union[str, tuple, list] = ("EG.PTMPositions", "EG.PTMProbabilities", "EG.PTMSites"),
):
    if isinstance(file_or_df, pd.DataFrame):
        title = file_or_df.columns.tolist()
    else:
        title = (
            rk.read_file_before_n_symbol(file_or_df, symbol="\n", n=1, openmode="r", encoding="utf8")
            .strip("\n")
            .split("\t")
        )
    ptms = []
    for t in title:
        if any([prefix in t for prefix in ptm_col_prefix]):
            for prefix in ptm_col_prefix:
                t = t.replace(prefix, "")
            ptms.append(t.strip(" "))
    return sorted(set(ptms))


def get_sn_report_ptm_dtypes(
    file_or_df_or_list,
    ptm_col_prefix: typing.Union[str, tuple, list] = ("EG.PTMPositions", "EG.PTMProbabilities", "EG.PTMSites"),
):
    """
    PTM position column like `EG.PTMPositions [Phospho (STY)]` could be single integer, or multi integers joined with `;`, or nan (e.g. `4;6;7;16`)
    PTM probability column like `EG.PTMProbabilities [Phospho (STY)]` could be single float, or multi floats joined with `;`, or nan (e.g. `0.14;0.03;0.81;0.03`)
    PTM sites column like `EG.PTMSites [Phospho (STY)]` could be single char, or multi chars joined with `;`, or nan (e.g. `S;Y;T;T`)

    :param file_or_df_or_list:
    :param ptm_col_prefix:
    :return:
    """
    if not isinstance(file_or_df_or_list, (list, set, tuple)):
        ptms = get_sn_report_ptms(file_or_df_or_list, ptm_col_prefix=ptm_col_prefix)
    else:
        ptms = file_or_df_or_list
    return dict(rk.sum_list([[(f"{prefix} {ptm}", "object") for prefix in ptm_col_prefix] for ptm in ptms]))


class SNMod(object):
    SNModToUnimod_13 = {""}

    def __init__(self, sn_version=14):
        if sn_version >= 13:
            self.sn_mod_to_unimod = self.SNModToUnimod_13
        else:
            pass

    def sn_modpep_to_unimod_pep(self):
        pass


class BasicModInfo(object):
    ModDict_new = {"C": "C[Carbamidomethyl (C)]", "M": "M[Oxidation (M)]"}
    ModDict_old = {"C": "C[Carbamidomethyl]", "M": "M[Oxidation]"}

    ModConvert_new = {}
    ModConvert_old = {}

    DeepRTIntModDict_new = {"C[Carbamidomethyl (C)]": "C", "M[Oxidation (M)]": "1", "S": "2", "T": "3", "Y": "4"}
    DeepRTIntModDict_old = {"C[Carbamidomethyl]": "C", "M[Oxidation]": "1", "S": "2", "T": "3", "Y": "4"}
    # IntModDict = {'M[+16]': '1', 'S[+80]': '2', 'T[+80]': '3', 'Y[+80]': '4'}

    pDeepModType = {"C": "Carbamidomethyl[C]", "M": "Oxidation[M]"}


class ModType(BasicModInfo):
    """
    Spectronaut version 12 has get_one_prefix_result different modification display type.
    The default version is set to 12, which uses the new modification display method.
    The version should be set in each main functions but not the functions that are used frequently.
    """

    def __init__(self, spectronaut_version=12):
        self._spectronaut_version = spectronaut_version
        self.ModDict = self.ModDict_new
        self.DeepRTIntModDict = self.DeepRTIntModDict_new

        self.pDeepMod2SNMod_new = dict([(self.pDeepModType[aa], self.ModDict_new[aa][1:]) for aa in self.pDeepModType])
        self.pDeepMod2SNMod_old = dict([(self.pDeepModType[aa], self.ModDict_old[aa][1:]) for aa in self.pDeepModType])
        self.pDeepMod2SNMod = self.pDeepMod2SNMod_new

    def set_spectronaut_version(self, version):
        self._spectronaut_version = version
        if self._spectronaut_version >= 12:
            self.ModDict = self.ModDict_new
            self.DeepRTIntModDict = self.DeepRTIntModDict_new
            self.pDeepMod2SNMod = self.pDeepMod2SNMod_new
        else:
            self.ModDict = self.ModDict_old
            self.DeepRTIntModDict = self.DeepRTIntModDict_old
            self.pDeepMod2SNMod = self.pDeepMod2SNMod_old

    def get_spectronaut_int_version(self):
        return self._spectronaut_version

    def get_spectronaut_str_version(self):
        if self._spectronaut_version >= 12:
            return "new"
        else:
            return "old"

    @staticmethod
    def get_mod_dict(ver="new"):
        if isinstance(ver, str):
            if ver == "new":
                return ModType.ModDict_new
            elif ver == "old":
                return ModType.ModDict_old
            else:
                raise NameError("Choose mod version from 'new' and 'old'")
        elif isinstance(ver, int):
            if ver >= 12:
                return ModType.ModDict_new
            else:
                return ModType.ModDict_old
