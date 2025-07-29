"""
Xwalk (version 0.6)
-------------------

INTRODUCTION
------------
Chemical cross-linking of proteins or protein complexes and the mass
spectrometry based localization of the cross-linked amino acids is a powerful
method for generating distance information on the substrate topology. Here we
introduce the algorithm Xwalk for predicting and validating these cross-links on
existing protein structures. Xwalk calculates and displays non-linear distances
between chemically cross-linked amino acids on protein surfaces, while mimicking
the flexibility and non-linearity of cross-linker molecules. It returns a
"Solvent Accessible Surface" (SAS) distance, which corresponds to the length of
the shortest path between two amino acids, where the path leads through solvent
occupied space without penetrating the protein surface.


TEST
-----
Test examples to execute Xwalk can be found in the test subdirectory.


CLASSPATH
---------
You might want to consider adding the bin directory into the CLASSPATH
environment of your SHELL, which avoids the usage of the -cp flag when executing
Xwalk.


COMMANDLINE PARAMETERS
----------------------
A list of all commandline parameters can be retrieved by typing -help before
a Xwalk execution.


OUTPUT
------
Distance information will be printed out to the STDOUT channel or via -out to a
local file in the following tab delimeted format:
...
1   1brs.pdb    LYS-1-D-CB  LYS-2-D-CB  1   5.9 6.6 0.0449  0.0685  KKAVINGEQIR-KAVINGEQIR
...
1st column: index
2nd column: filename
3rd column: PDB information of the 1st amino acid in the format:
            PDBThreeLetterCode-ResidueId-ChainId-AtomName
4th column: PDB information of the 2nd amino acid in the format:
            PDBThreeLetterCode-ResidueId-ChainId-AtomName
5th column: Sequence distance within the PDB file as calculated from the residue
            identifiers of the 1st and 2nd amino acid.
6th column: Euclidean distance between 1st and 2nd amino acid.
7th column: SAS distance between  1st and 2nd amino acid.
8th column: Probability for observing the Euclidean distance in a XL experiment
            using DSS or BS3.
9th column: Probability for observing the SAS distance in a XL experiment using
            DSS or BS3.
10th column: shortest tryptic peptide sequence for both amino acids.

Setting -pymol -out xxx.pml on the commandline will write a PyMOL script into
the file xxx.pml, which can be load into the molecular viewer PyMOL to visualise
the SAS distance paths (see NOTES).


ALGORITHM
---------
The SAS distance is calculated using a grid and the breadth-first search algorithm
to search within the grid for the shortest path between two points on the protein
surface using following algorithm:
1.)    Read in input data
    a. xyz.pdb, spatial coordinates of a protein or protein complex in PDB
       format.
    b. maxdist: maximum distance of the path (i.e. the length of the
       cross-linker + AA side chain length)
    c. listXL, a list of experimentally determined cross-linked lysine residues.
2.)    Remove all non-protein atoms in xyz.pdb and assign protein atoms a van der
    Waals radius sum of SURFNET atom radii + solvent radius
3.)    Select a random lysine pair AAab from listXL,
4.)    Check Euclidean distance (Euc) of AAab. Continue, if Euc > maxdist,
    disregard otherwise and go back to 3.)
5.)    Generate a grid of size maxdist and grid spacing 1 Angstroem centered at AAa
6.)    Set Integer.MAX_VALUE as distance for all grid cells and label grid cells as
    residing in the
    a. protein
    b. solvent
    c. boundary between protein and solvent
7.)    Label grid cells residing in AAab as solvent
8.)    Set distance dist = 0.0 for central grid cell of AAa and store grid cell in
    the active list listactive
9.)    Start breadth-first search. Iterate through listactive
    a. Check that grid cell i is labeled as solvent
    b. Find all immediate neighbors listneighbour
    c. Iterate through listneighbour
        i. Check that grid cell j is labeled as solvent
        ii. Compute new distance for grid cell j as the sum of the distance in
            grid cell i and the Euclidean distance between grid cell i and j
        iii. If distance sum in 9.c.ii is smaller than the current distance in
             grid cell j, store the distance sum as new distance for grid cell j
             and add grid cell j to the new active list listnew_active,
10.) Go back to step 9.) with listactive = listnew_active



NOTES
-----
- As the SAS distance is based on a grid calculation, the default heap size of
  the Java VM with 64MB is likely to be too small. You can increase the heap
  size with "java -Xmx512m"
- You can obtain PyMOL for free at the webpage: http://pymol.org/
- Beware that in order for PyMOL to recognize the script file, the file must
  have the name ending .pml
- You can load the script directly at the startup of PyMOL, i.e. with the
  command pymol 1brs.pml.


CONTACT
-------
abdullah@imsb.biol.ethz.ch


LICENCE
-------
Xwalk executable and libraries are available under the Creative Commons
Attribution-NonCommercial-ShareAlike 3.0 Unported License via the Xwalk website.

Anyone is free:
     to copy, modify, distribute the software;

Under the following conditions:
    - the original authors must be given credit by citing the original Xwalk paper:
        Kahraman A., Malmström L., Aebersold R. (2011). Xwalk: Computing and
        Visualizing Distances in Cross-linking Experiments. Bioinformatics,
        doi:10.1093/bioinformatics/btr348.
    - the software or derivate works must not be used for commercial purposes
    - derivate works must be licenced under the same or similar licence

Any of the above conditions can be waived if the authors give permission.


Xwalk on GitHub
---------------
https://github.com/abxka/Xwalk


COMMAND EXAMPLES
----------------
    # Help with information on the available parameter
java -cp ../bin/ Xwalk -help

    # Example executions on the barnase-barstar complex 1brs.pdb.
    # Calculate the Euclidean distance (-euc)
    # between the closest atoms of lysine residue (-aa1 lys -aa2 lys)
    # that have a maximum distance of 30 Angstroem.
java -cp ../bin/ Xwalk -infile 1brs.pdb -aa1 lys -aa2 lys -euc

    # Calculate the Euclidean distance (-euc)
    # between the closest atoms of aspartic (-aa1 asp) and glutamic (-aa2 glu) acid residues
    # that have a maximum distance of 30 Angstroem.
java -cp ../bin/ Xwalk -infile 1brs.pdb -aa1 asp -aa2 glu -euc -max 21.4

    # Calculate SASD
    # between beta-carbon atoms (-a1 cb -a2 cb)
    # of lysine residues (-aa1 lys -aa2 lys).
    # that have a maximum distance of 21.4 Angstroem (-max 21.4).
    # and remove prior to calculation all side chains (-bb)
java -Xmx256m -cp ../bin/ Xwalk -infile 1brs.pdb -aa1 lys -aa2 lys -a1 cb -a2 cb -max 21.4 -bb

    # Calculate SASD of intermolecular cross-links (-inter)
    # between the epsilon-nitrogen atoms (-a1 nz -a2 nz)
    # of lysine residues (-aa1 lys -aa2 lys).
    # that have a maximum distance of 11.4 Angstroem (-max 11.4).
    # and remove prior to calculation all side chains (-bb)
    # and output PyMOL script to visualize the SASD path (-pymol -out 1brs.pml)
java -Xmx256m -cp ../bin/ Xwalk -infile 1brs.pdb -aa1 lys -aa2 lys -a1 nz -a2 nz -max 21.4 -inter -pymol -out 1brs.pml


Xwalk HELP MESSAGE
------------------
EXAMPLARY command for program execution:
Xwalk -in 1brs.pdb -aa1 ARG -aa2 lys -a1 CB -a2 CB -bb -max 21

ABOUT
Version 0.6
Xwalk calculates and outputs distances in Angstroem for potential cross-links
between -aa1 type amino acids and -aa2 type amino acids in the PDB file -in.

IMPORTANT
If large protein complexes are processed, the Java heap size might need to be
increased from the default 64MB to 256MB, with the Java parameter -Xmx256m

OUTPUT FORMAT:
IndexNo InfileName      Atom1info       Atom2info       DistanceInPDBsequence   EuclideanDistance       SolventAccessibleSurfaceDistance        EucProbability  SASDprobability PeptidePairSequences

where the Solvent Accessible Surface (SAS) distance corresponds to a number code, when a Distance file (-dist) is provided:
        >= 0: SAS distance (when -euc is NOT set)
        -1: Distance exceeds the maximum distance (-max)
        -2: First atom is solvent-inaccessible
        -3: Second atom is solvent-inaccessible
        -4: Both atoms are solvent-inaccessible
        -5: First atom is in a cavity which prohibited proper shortest path calculations


Virtual cross-links are sorted first by decreasing probability, then by increasing SAS distance and finally by increasing Euclidean distance.

Commandline PARAMETER:
INPUT/OUTPUT:
        -infile <path>  Any PDB file; .tar, .gz and .tar.gz files with PDB file content are also accepted [required].
        -xSC    [switch]        Removes only side chain atoms of cross-linked amino acids except for CB atoms and keeps -radius at 1.4 prior to calculating SAS distances. This might be of value when side chain conformations of cross-linked residues are unknown [optional].
        -bb     [switch]        Reads in only backbone and beta carbon atom coordinates from the input file and increases -radius to 2.0. Be cautious using the option, as it might cause shortest path calculalations through "molecular tunnels" in your protein [optional][see also -xSC].
        -dist   <path>  Distance file holding at least the first 4 columns of the Xwalk output format. The file will be used to extract the indices and the residue pairs for the distance calculation [optional].
        -keepName       [switch]        Uses the same name (2nd column) in the output as in the distance file. [optional].
        -out    <path>  Writes output to this file, otherwise output is directed to the STDOUT channel. If -pymol is set than filename must have .pml filename ending [optional].
        -f      [switch]        Forces output to be written into a file even if file already exists [optional].
        -pymol  [switch]        Outputs a PyMOL (http://www.pymol.org/) script highlighting the calculated distances of the potential cross-links [optional].
        -v      [switch]        Outputs various information other than distances [optional].
        -grid   [switch]        Outputs on STDOUT channel the grid, which is used to calculate the Solvent Accessible Surface Distance. The grid is in PDB format with distances in the B-factor column [optional].

RESIDUE/ATOM SELECTION:
        -aa1    [String]        Three letter code of 1st amino acid. To specify more than one amino acid use '#' as a delimeter [required, if -r1 is not set].
        -aa2    [String]        Three letter code of 2nd amino acid. To specify more than one amino acid use '#' as a delimeter [required, if -r2 is not set].
        -r1     [String]        Amino acid residue number. To specify more than one residue number use '#' as a delimeter. [required, if -aa1 is not set].
        -r2     [String]        Amino acid residue number. To specify more than one residue number use '#' as a delimeter. [required, if -aa2 is not set].
        -c1     [String]        Chain ids for -aa1 or -r1. For blank chain Id use '_'. To specify more than one chain Id, append chain ids to a single string, e.g. ABC [optional](default: all chain Ids).
        -c2     [String]        Chain ids for -aa2 or -r2. For blank chain Id use '_'. To specify more than one chain Id, append chain ids to a single string, e.g. ABC [optional](default: all chain Ids).
        -a1     [String]        Atom type for -aa1 or -r1. To specify more than one atom type use '#' as a delimeter. [optional].
        -a2     [String]        Atom type for -aa2 or -r2. To specify more than one atom type use '#' as a delimeter. [optional].
        -l1     [String]        Alternative location id for -aa1 or -r1. To specify more than one alternative location, append alternative location ids to a single string, e.g. AB [optional].
        -l2     [String]        Alternative location id for -aa2 or -r1. To specify more than one alternative location, append alternative location ids to a single string, e.g. AB [optional].
        -intra  [switch]        Outputs only "intra-molecular" distances [optional].
        -inter  [switch]        Outputs only "inter-molecular" distances [optional].
        -homo   [double]        Outputs only shortest distance of potential cross-links between equally numbered residues. Reduces redundancy if PDB file is a homomeric protein complex. [optional].

DIGESTION RELATED:
        -trypsin        [switch]        Digests in silico the protein with trypsin and excludes peptides that are shorter than 5 AA or larger than 40 AA [optional].

DISTANCE RELATED:
        -max    [double]        Calculates distances in Angstroem only up-to this value, where the value must be smaller than 100.0 for SAS distance calculations. (default: 34.0).
        -euc    [switch]        Skips Solvent-Path-Distance calculation and outputs only Euclidean distances [optional].
        -prob   [switch]        Outputs probability information for each vXL as determined by experimental data on DSS and BS3 cross-linking experiments [optional].
        -bfactor        [switch]        Adds the uncertainty of the atom coordinates as expressed by their B-factor/temperature factor to the maximum distance threshold [optional].

SOLVENT-PATH-DISTANCE GRID RELATED:
        -radius [double]        Solvent radius for calculating the solvent accessible surface area [optional](default 1.4).
        -space  [double]        Spacing in Angstroem between grid cells. [optional](default 1.0).

"""

import os
import re
import subprocess
import threading
import time
import traceback
import typing

import numpy as np
import pandas as pd

from mskit import multi_kits as rk
from mskit.constants.aa import AA
from mskit.sequence.fasta import read_fasta

try:
    import wx
except ModuleNotFoundError:
    pass


def extract_xwalk_cmd(xwalk_cmd):
    aa1 = re.findall("-aa1 (.+?) ", xwalk_cmd, re.I)[0]
    aa2 = re.findall("-aa2 (.+?) ", xwalk_cmd, re.I)[0]
    a1 = re.findall("-a1 (.+?) ", xwalk_cmd, re.I)[0]
    a2 = re.findall("-a2 (.+?) ", xwalk_cmd, re.I)[0]
    inter_intra = re.findall("-(inter|intra)", xwalk_cmd, re.I)
    inter_intra = inter_intra[0] if inter_intra else None
    max_length = re.findall(r"-max (\d+?)[> ]", xwalk_cmd, re.I)[0]
    return aa1, aa2, a1, a2, inter_intra, max_length


def read_command_file(cmd_file, pdb_name):
    cmd_list = []
    with open(os.path.abspath(cmd_file), "r") as cmd_handle:
        for each_line in cmd_handle:
            each_cmd = each_line.strip("\n")
            if not each_cmd:
                continue
            aa1, aa2, a1, a2, inter_intra, maxlength = extract_xwalk_cmd(each_cmd)

            rearranged_cmd = "java -Xmx1024m Xwalk -infile {}.pdb -aa1 {} -aa2 {} -a1 {} -a2 {}{} -max {} -bb >".format(
                pdb_name, aa1, aa2, a1, a2, " -{}".format(inter_intra) if inter_intra else "", maxlength
            )
            out_filename = "{pdb_filename}-{aa1}_{aa2}_{a1}_{a2}{inter_intra}-{maxlength}.txt".format(
                pdb_filename=pdb_name,
                aa1=aa1,
                aa2=aa2,
                a1=a1,
                a2=a2,
                inter_intra="-{}".format(inter_intra) if inter_intra else "",
                maxlength=maxlength,
            )

            cmd_list.append((rearranged_cmd, out_filename))
    return cmd_list


def xwalk_run(cmd_list, result_add):
    cmd_num = len(cmd_list)
    for cmd_series, _ in enumerate(cmd_list):
        rearranged_cmd, out_filename = _
        each_cmd = '{}"{}"'.format(rearranged_cmd, os.path.join(result_add, out_filename))
        print("{}/{} Now running {}".format(cmd_series + 1, cmd_num, each_cmd))
        os.system(each_cmd)


def merge_result(result_add):
    result_file_list = os.listdir(result_add)
    file_num = len(result_file_list)
    with (
        open(os.path.join(result_add, "MergedIntra.txt"), "w") as intra_handle,
        open(os.path.join(result_add, "MergedInter.txt"), "w") as inter_handle,
    ):
        for file_series, each_result in enumerate(result_file_list):
            print("{}/{} Merging {}".format(file_series + 1, file_num, each_result))
            intra_handle.write(each_result + "\n")
            inter_handle.write(each_result + "\n")

            result_path = os.path.join(result_add, each_result)
            with open(result_path, "r") as result_handle:
                for each_line in result_handle:
                    if not each_line.strip("\n"):
                        continue
                    split_line = each_line.split("\t")
                    first_site = split_line[2]
                    second_site = split_line[3]
                    if first_site.split("-")[2] == second_site.split("-")[2]:
                        intra_handle.write(each_line)
                    else:
                        inter_handle.write(each_line)
            intra_handle.write("\n")
            inter_handle.write("\n")


class SiteConverter(object):
    def __init__(
        self,
        logger=None,
    ):
        """
        TODO change names of PDB and FASTA to Alternative and Standard
        FASTA-PDB site mapper
        """
        self.logger = logger

        self._aa_3to1 = {k.upper(): v.upper() for k, v in AA.AA_3to1.items()}
        self._aa_1to3 = {k.upper(): v.upper() for k, v in AA.AA_1to3.items()}

        self.conversion_tables: typing.Dict[str, pd.DataFrame] = dict()
        self.converter_num: int = 0

        self._pdb_site: typing.Dict[str, list] = dict()
        self._fasta_site: typing.Dict[str, list] = dict()
        self._aa3: typing.Dict[str, list] = dict()

    def set_logger(self, logger):
        self.logger = logger

    def _parse_conversion_input(self, conversion_input, exclude=None, name=None) -> typing.Dict[str, pd.DataFrame]:
        if isinstance(conversion_input, pd.DataFrame):
            if name is None:
                raise ValueError(f"A name should be assigned to site converter if pd.DataFrame is transferred")
            return {name: conversion_input}
        elif isinstance(conversion_input, str):
            if os.path.isdir(conversion_input):
                files = {
                    os.path.splitext(file)[0]: os.path.join(conversion_input, file)
                    for file in os.listdir(conversion_input)
                    if file not in exclude
                }
            elif os.path.isfile(conversion_input):
                if conversion_input in exclude:
                    files = {}
                elif name is None:
                    files = {os.path.splitext(os.path.basename(conversion_input))[0]: conversion_input}
                else:
                    files = {name: conversion_input}
            else:
                raise ValueError(f"Input conversion data is neither file or folder, nor a pd.DataFrame")
            if self.logger is not None:
                self.logger.info(f"SiteConverter will load conversion files: {conversion_input}")
            dfs = dict()
            for name, file in files.items():
                df = rk.pd_load_file_to_df(
                    file,
                    load_all_sheets=True,
                    custom_raise_for_other_formats=ValueError(
                        f"Input file for PDB-FASTA site conversion should have format "
                        f"in `.xlsx, .xls, .txt, .tsv, .csv`. Now {os.path.basename(file)}"
                    ),
                    dtype=str,
                )
                if isinstance(df, pd.DataFrame):
                    dfs[name] = df
                elif isinstance(df, dict):
                    dfs.update(df)
                else:
                    raise ValueError
            return dfs
        else:
            raise ValueError(f"Only a file path or pd.DataFrame is valid for SiteConverter")

    def _parse_conversion_table(
        self,
        dfs: typing.Dict[str, pd.DataFrame],
        pdb_site_col_name: str = "PDB",
        fasta_site_col_name: str = "FASTA",
        aa_col_name: str = "AA3",
        aa_type: str = "AA3",
        fasta_file: str = None,
    ):
        for name, df in dfs.items():
            if self.logger is not None:
                self.logger.info(f"SiteConverter parsing conversion table: {name}")
            if pdb_site_col_name not in df.columns or fasta_site_col_name not in df.columns:
                raise ValueError(
                    f"Columns {pdb_site_col_name} and {fasta_site_col_name} are assigned to AA position for `PDB` and `FASTAS`,"
                    f"but the columns are not complete"
                )
            df = df.copy()
            df[[pdb_site_col_name, fasta_site_col_name]] = df[[pdb_site_col_name, fasta_site_col_name]].astype(int)
            df = df.replace("", np.nan)
            df = df.dropna(axis=0, how="any", subset=[pdb_site_col_name, fasta_site_col_name])

            if fasta_file is not None:
                fasta = read_fasta(fasta_file, sep=">", ident_idx=1)
                df["AA1"] = df[fasta_site_col_name].apply(lambda x: fasta[x - 1])
                aa_col_name = "AA1"
                aa_type = "AA1"
            if aa_type == "AA1":
                df["AA3"] = df[aa_col_name].map(self._aa_1to3)
                aa_col_name = "AA3"
            elif aa_type != "AA3":
                raise ValueError(f"aa_type should be either AA1 or AA3. Now {aa_type}")

            self._pdb_site[name] = df[pdb_site_col_name].tolist()
            self._fasta_site[name] = df[fasta_site_col_name].tolist()
            self._aa3[name] = df[aa_col_name].tolist()

    def add_converter(
        self,
        conversion_input: typing.Union[str, pd.DataFrame],
        exclude=("ProteinIdentifierMatch.xlsx",),
        name: str = None,
        pdb_site_col_name: str = "PDB",
        fasta_site_col_name: str = "FASTA",
        aa_col_name: str = "AA3",
        aa_type: str = "AA3",
        fasta_file: str = None,
    ):
        """
        Either `fasta_file` or (`aa_col_name` and `aa_type`) should be provided
        """
        if self.logger is not None:
            self.logger.info(f"SiteConverter adding conversion input: {conversion_input}")
        dfs = self._parse_conversion_input(conversion_input, exclude=exclude, name=name)
        self.conversion_tables.update(dfs)
        self._parse_conversion_table(
            dfs=dfs,
            pdb_site_col_name=pdb_site_col_name,
            fasta_site_col_name=fasta_site_col_name,
            aa_col_name=aa_col_name,
            aa_type=aa_type,
            fasta_file=fasta_file,
        )
        self.refresh_converter_num()

    def refresh_converter_num(self):
        self.converter_num = len(self._pdb_site)

    def __getitem__(self, item):
        try:
            return self._pdb_site[item], self._fasta_site[item], self._aa3[item]
        except IndexError:
            raise IndexError(f"{item} has not been added to SiteConverter")

    def pdb_to_fasta(self, pdb_pos, name=None):
        if name is None and self.converter_num == 1:
            name = list(self._pdb_site.keys())[0]
        try:
            idx = self._pdb_site[name].index(pdb_pos)
            return self._fasta_site[name][idx], self._aa3[name][idx]
        except ValueError:
            if self.logger is not None:
                self.logger.info(f"SiteConverter can not find PDB position {pdb_pos} in {name}")
            return None
        except KeyError:
            raise KeyError(
                f'No protein named "{name}" when converting this protein from PDB to FASTA. This protein should be defined in protein identifier conversion table'
            )

    def fasta_to_pdb(self, fasta_pos, name=None):
        if name is None and self.converter_num == 1:
            name = list(self._fasta_site.keys())[0]
        try:
            idx = self._fasta_site[name].index(fasta_pos)
            return self._pdb_site[name][idx], self._aa3[name][idx]
        except ValueError:
            if self.logger is not None:
                self.logger.info(f"SiteConverter can not find FASTA position {fasta_pos} in {name}")
            return None
        except KeyError:
            raise KeyError(
                f'No protein named "{name}" when converting this protein from FASTA to PDB. This protein would be expected to be a `standard protein identifer`'
            )


class XwalkRunner(object):
    xwalk_command_template = (
        'java -Xmx1024m -cp "{xwalk_bin}" Xwalk'
        ' -infile "{pdb_path}"'
        ' -pymol -out "{pymol_output}"'
        ' -dist "{xwalk_input_file}"'
        " -max {max_distance} -bb -homo"
        ' >"{output_path}"'
    )
    xwalk_output_title = (
        "IDX",
        "PDBFileName",
        "AA_1",
        "AA_2",
        "PDBSeqDist",
        "Euclidean",
        "SAS",
        "Prob_Euclidean_DSS_BS3",
        "Prob_SAS_DSS_BS3",
        "ShortestTypPep",
    )
    linker_linked_aa = {
        "ArGO": (("Arg", "Arg"),),
        "KArGO": (("Lys", "Arg"),),
        "EGS": (("Lys", "Lys"),),
        "DSS": (("Lys", "Lys"),),
        "BS3": (("Lys", "Lys"),),
        "PDH": (("Glu", "Asp"), ("Glu", "Glu"), ("Asp", "Asp")),
        "EDC": (("Lys", "Glu"), ("Lys", "Asp")),
    }

    def __init__(
        self,
        xwalk_input_file_path=None,
        pdb_path=None,
        xwalk_output_path=None,
        logger=None,
        linker_aa_file=None,
    ):
        self._xwalk_input_file_path = xwalk_input_file_path
        self._pdb_path = pdb_path
        self._xwalk_output_path = xwalk_output_path
        self._result_df = None

        self.logger = logger

        if linker_aa_file is not None:
            self._read_linker_linking_info(linker_aa_file)

    def set_logger(self, logger):
        self.logger = logger

    def generate_xwalk_input(
        self,
        xwalk_pdb_pos_pair: list,
        pdb_filename: str = None,
        output_path: str = None,
    ):
        """
        :param xwalk_pdb_pos_pair: list of xwalk used position pairs with protein and position in PDB scale,
                                   like [('LYS-338-A-CA', 'SER-352-A-CA), (...), ...]
        :param pdb_filename: filename of used PDB file, like 0409-GLP-1R.pdb
        :param output_path:
        """
        if self.logger is not None:
            self.logger.info(
                f"XwalkRunner generating xwalk input, with {len(xwalk_pdb_pos_pair)} pairs, PDB file {pdb_filename}, and output to {output_path}"
            )
        if pdb_filename is None:
            pdb_filename = os.path.basename(self._pdb_path)

        xwalk_input = []
        for idx, pair in enumerate(xwalk_pdb_pos_pair, 1):
            xwalk_input.append("{}\t{}\t{}\t{}\n".format(idx, pdb_filename, *pair))

        xwalk_input = rk.drop_list_duplicates(xwalk_input)
        if self.logger is not None:
            self.logger.info(f"XwalkRunner final non-redundant xwalk input, with {len(xwalk_input)} pairs")

        if output_path is None:
            output_path = self._xwalk_input_file_path
        else:
            self._xwalk_input_file_path = output_path

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write("".join(xwalk_input))

    def generate_xwalk_command(
        self,
        xwalk_bin,
        pymol_output,
        xwalk_input_file,
        max_distance,
        pdb_path: str = None,
        output_path: str = None,
    ):
        if pdb_path is None:
            pdb_path = self._pdb_path
        else:
            self._pdb_path = pdb_path

        if output_path is None:
            output_path = self._xwalk_output_path
        else:
            self._xwalk_output_path = output_path

        command = self.xwalk_command_template.format(
            xwalk_bin=xwalk_bin,
            pdb_path=pdb_path,
            pymol_output=pymol_output,
            xwalk_input_file=xwalk_input_file,
            max_distance=max_distance,
            output_path=output_path,
        )

        os.makedirs(os.path.dirname(self._xwalk_output_path), exist_ok=True)

        if self.logger is not None:
            self.logger.info(f"XwalkRunner generated xwalk command: `{command}`")
        return command

    def run_xwalk(self, command, new_thread=False, gui_window=None, **params):
        if command is None:
            command = self.generate_xwalk_command(**params)
        if "output_path" in params:
            os.makedirs(os.path.dirname(params["output_path"]), exist_ok=True)

        if new_thread:
            runner_thread = XwalkRunnerThread(name=None, logger=self.logger, window=gui_window)
            runner_thread.setDaemon(True)
            runner_thread.set_cmd(command)
            runner_thread.start()
            runner_thread.join()
        else:
            if self.logger is not None:
                self.logger.info(f"XwalkRunner start running command: `{command}`")
            code = os.system(command)
            if code == -1:
                raise RuntimeError(f"Xwalk failed")

        if self.logger is not None:
            self.logger.info(f"XwalkRunner Xwalk completed")

    def collect_results(self, path=None):
        if path is None:
            path = self._xwalk_output_path
        if self.logger is not None:
            self.logger.info(f"XwalkRunner collecting result from {path}")

        self._result_df = pd.read_csv(path, sep="\t", low_memory=False, header=None)
        self._result_df.columns = self.xwalk_output_title
        return self._result_df

    def _read_linker_linking_info(self, linker_aa_file):
        with open(linker_aa_file, "r") as f:
            linker_info = f.read().split("\n")
        for row in linker_info:
            if "linker" in row:
                continue
            elif not row:
                continue
            else:
                split_row = row.split(",")
                if len(split_row) <= 1:
                    continue
                self.linker_linked_aa[split_row[0]] = (
                    (split_row[aa_num * 2], split_row[aa_num * 2 + 1]) for aa_num in range(len(split_row[1:]) // 2)
                )


class XwalkRunnerThread(threading.Thread):
    def __init__(self, name=None, logger=None, window=None, *args, **kwargs):
        super(XwalkRunnerThread, self).__init__(*args, **kwargs)

        if name is None:
            name = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())

        self.logger = logger
        self.window = window

        self.runner_process = None
        self.cmd = None
        self.terminated = False

    def set_logger(self, logger):
        self.logger = logger

    def set_cmd(self, cmd):
        if self.logger is not None:
            self.logger.info(f"XwalkRunnerThread {self.name} set command as `{cmd}`")
        self.cmd = cmd

    def run(self):
        if self.logger is not None:
            self.logger.info(f"XwalkRunnerThread start thread")
        self.terminated = False
        try:
            if self.logger is not None:
                self.logger.info(f"XwalkRunnerThread {self.name} start. Command: `{self.cmd}`")
            self.runner_process = subprocess.Popen(self.cmd)
            self.runner_process.wait()
            if self.terminated:
                pass
            elif self.runner_process.poll() is None:
                raise ValueError("Xwalk is still running")
            elif self.runner_process.poll() == 0:
                if self.window is not None:
                    wx.CallAfter(self.window.running_done)
                if self.logger is not None:
                    self.logger.info(f"XwalkRunnerThread Xwalk task {self.name} finished")
            else:
                if self.window is not None:
                    wx.CallAfter(self.window.running_error)
                if self.logger is not None:
                    self.logger.error(f"XwalkRunnerThread Xwalk task {self.name} error")
        except Exception:
            tb = traceback.format_exc()
            if self.logger is not None:
                self.logger.error(f"XwalkRunnerThread Xwalk task {self.name} error: {tb}")
            if self.window is not None:
                wx.CallAfter(self.window.running_error)
            else:
                raise Exception
        finally:
            self.terminated = False

    def terminate(self):
        self.runner_process.terminate()
        self.terminated = True
        if self.window is not None:
            wx.CallAfter(self.window.running_cancel)
        if self.logger is not None:
            self.logger.error(f"XwalkRunnerThread Xwalk task {self.name} terminated")
