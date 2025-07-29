""" """
import polars as pl

DIANN_OutputDtype = {
    # File
    "File.Name": "str",
    "Run": "str",

    # Protein
    "Protein.Group": "str",
    "Protein.Ids": "str",
    "Protein.Names": "object",
    "PG.Quantity": "float64",
    "PG.Normalised": "float64",
    "PG.MaxLFQ": "float64",
    "Protein.Q.Value": "float64",
    "PG.Q.Value": "float64",
    "Global.PG.Q.Value": "float64",
    "First.Protein.Description": "object",
    "Lib.PG.Q.Value": "float64",

    # Gene
    "Genes": "object",
    "Genes.Quantity": "float64",
    "Genes.Normalised": "float64",
    "Genes.MaxLFQ": "float64",
    "Genes.MaxLFQ.Unique": "float64",
    "GG.Q.Value": "float64",

    # Peptide
    "Modified.Sequence": "str",
    "Stripped.Sequence": "str",
    "Precursor.Id": "str",
    "Precursor.Charge": "int",
    "Precursor.Mz": "float64",
    "Proteotypic": "int64",
    "Precursor.Quantity": "float64",
    "Precursor.Normalised": "float64",
    "Precursor.Translated": "float64",
    "Normalisation.Factor": "float64",

    # Stats & Scores
    "Q.Value": "float64",
    "PEP": "float64",
    "Global.Q.Value": "float64",
    "Translated.Q.Value": "float64",
    "Lib.Q.Value": "float64",
    "Mass.Evidence": "float64",
    "Evidence": "float64",
    "CScore": "float64",
    "Decoy.Evidence": "float64",
    "Decoy.CScore": "float64",

    # Spec
    "Ms1.Profile.Corr": "float64",
    "Spectrum.Similarity": "float64",
    "Fragment.Quant.Raw": "object",
    "Fragment.Quant.Corrected": "object",
    "Fragment.Correlations": "object",
    "MS2.Scan": "int64",
    "Quantity.Quality": "float64",
    "Ms1.Area": "float64",
    "Ms1.Normalised": "float64",
    "Ms1.Translated": "float64",
    "Fragment.Info": "str",

    # PTM
    "PTM.Informative": "float64",
    "PTM.Specific": "float64",
    "PTM.Localising": "float64",
    "PTM.Q.Value": "float64",
    "PTM.Site.Confidence": "float64",
    "Lib.PTM.Site.Confidence": "float64",

    # RT
    "RT": "float64",
    "iRT": "float64",
    "RT.Start": "float64",
    "RT.Stop": "float64",
    "Predicted.RT": "float64",
    "Predicted.iRT": "float64",

    # IM
    "IM": "float64",
    "iIM": "float64",
    "Predicted.IM": "float64",
    "Predicted.iIM": "float64",

    # Others
    "Averagine": "float64",
    "Lib.Index": "int64",
}

DIANN_TsvLibDtype = {
    "FileName": "object",
    "PrecursorMz": "float64",
    "ProductMz": "float64",
    "Tr_recalibrated": "float64",
    "IonMobility": "float64",
    "transition_name": "object",
    "LibraryIntensity": "float64",
    "transition_group_id": "object",
    "decoy": "int64",
    "PeptideSequence": "object",
    "Proteotypic": "int64",
    "QValue": "float64",
    "PGQValue": "float64",
    "Ms1ProfileCorr": "float64",
    "ProteinGroup": "object",
    "ProteinName": "object",
    "Genes": "object",
    "FullUniModPeptideName": "object",
    "ModifiedPeptide": "object",
    "PrecursorCharge": "int64",
    "PeptideGroupLabel": "object",
    "UniprotID": "object",
    "NTerm": "int64",
    "CTerm": "int64",
    "FragmentType": "object",
    "FragmentCharge": "int64",
    "FragmentSeriesNumber": "int64",
    "FragmentLossType": "object",
    "ExcludeFromAssay": "bool",
}

DIANN_OutputDtype_PL = {
    # File
    "File.Name": pl.String,
    "Run": pl.String,

    # Protein
    "Protein.Group": pl.String,
    "Protein.Ids": pl.String,
    "Protein.Names": pl.String,
    "PG.Quantity": pl.Float64,
    "PG.Normalised": pl.Float64,
    "PG.MaxLFQ": pl.Float64,
    "Protein.Q.Value": pl.Float64,
    "PG.Q.Value": pl.Float64,
    "Global.PG.Q.Value": pl.Float64,
    "First.Protein.Description": pl.String,
    "Lib.PG.Q.Value": pl.Float64,

    # Gene
    "Genes": pl.String,
    "Genes.Quantity": pl.Float64,
    "Genes.Normalised": pl.Float64,
    "Genes.MaxLFQ": pl.Float64,
    "Genes.MaxLFQ.Unique": pl.Float64,
    "GG.Q.Value": pl.Float64,

    # Peptide
    "Modified.Sequence": pl.String,
    "Stripped.Sequence": pl.String,
    "Precursor.Id": pl.String,
    "Precursor.Charge": pl.Int16,
    "Precursor.Mz": pl.Float64,
    "Proteotypic": pl.Int16,
    "Precursor.Quantity": pl.Float64,
    "Precursor.Normalised": pl.Float64,
    "Precursor.Translated": pl.Float64,
    "Normalisation.Factor": pl.Float64,

    # Stats & Scores
    "Q.Value": pl.Float64,
    "PEP": pl.Float64,
    "Global.Q.Value": pl.Float64,
    "Translated.Q.Value": pl.Float64,
    "Lib.Q.Value": pl.Float64,
    "Mass.Evidence": pl.Float64,
    "Evidence": pl.Float64,
    "CScore": pl.Float64,
    "Decoy.Evidence": pl.Float64,
    "Decoy.CScore": pl.Float64,

    # Spec
    "Ms1.Profile.Corr": pl.Float64,
    "Spectrum.Similarity": pl.Float64,
    "Fragment.Quant.Raw": pl.String,
    "Fragment.Quant.Corrected": pl.String,
    "Fragment.Correlations": pl.String,
    "MS2.Scan": pl.Int64,
    "Quantity.Quality": pl.Float64,
    "Ms1.Area": pl.Float64,
    "Ms1.Normalised": pl.Float64,
    "Ms1.Translated": pl.Float64,
    "Fragment.Info": pl.String,

    # PTM
    "PTM.Informative": pl.Float64,
    "PTM.Specific": pl.Float64,
    "PTM.Localising": pl.Float64,
    "PTM.Q.Value": pl.Float64,
    "PTM.Site.Confidence": pl.Float64,
    "Lib.PTM.Site.Confidence": pl.Float64,

    # RT
    "RT": pl.Float64,
    "iRT": pl.Float64,
    "RT.Start": pl.Float64,
    "RT.Stop": pl.Float64,
    "Predicted.RT": pl.Float64,
    "Predicted.iRT": pl.Float64,

    # IM
    "IM": pl.Float64,
    "iIM": pl.Float64,
    "Predicted.IM": pl.Float64,
    "Predicted.iIM": pl.Float64,

    # Others
    "Averagine": pl.Float64,
    "Lib.Index": pl.Int64,
}
