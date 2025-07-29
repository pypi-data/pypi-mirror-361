import copy
import os
import re
import typing
from collections import defaultdict
from os.path import join as join_path

import numpy as np
import pandas as pd

from mskit import multi_kits as rk


def extract_prot_link_info(x):
    prot_link = re.findall(r"(.+?)?\((\d+)\)-?", x)
    if len(prot_link) not in [1, 2]:
        raise ValueError(f"Failed to parse protein link pair: {x}")

    prot_1, site_1 = prot_link[0]
    if len(prot_link) == 1:
        prot_2, site_2 = None, None
    else:
        prot_2, site_2 = prot_link[1]
        if prot_2 == "" or prot_2 is None:
            prot_2 = prot_1

    prot_link_site_need_sort = False
    if prot_2 is not None:
        if int(site_1) > int(site_2):
            prot_link_site_need_sort = True
    return prot_1, prot_2, site_1, site_2, prot_link_site_need_sort


def extract_pep_link_info(x):
    pep_link = re.findall(r"(.+?)?\((\d+)\)-?", x["Peptide"])
    if len(pep_link) not in [1, 2]:
        raise ValueError(f'Failed to parse peptide link pair: {x["Peptide"]}')

    pep_1, site_1 = pep_link[0]
    if len(pep_link) == 1:
        pep_2, site_2 = None, None
    else:
        pep_2, site_2 = pep_link[1]
        if pep_2 == "" or pep_2 is None:
            pep_2 = pep_1
    return pep_1, pep_2, site_1, site_2


def combine_id_link_info(id1: str, id2: str, site1, site2, reverse_site: bool):
    if id2 is not None:
        if reverse_site:
            sorted_link = f"{id2}({site2})-{id1}({site1})"
        else:
            sorted_link = f"{id1}({site1})-{id2}({site2})"
    else:
        sorted_link = f"{id1}({site1})"
    return sorted_link


class PLinkResult(object):
    def __init__(self, logger=None):
        self._plink_result_path = defaultdict(dict)

        self._plink_results = defaultdict(dict)
        self._merged_result = None
        self._merged_result_backup = None

        self.logger = logger

    def set_logger(self, logger):
        self.logger = logger

    def collect_plink_result_paths(self, dir_) -> None:
        """auto-collect"""
        if self.logger is not None:
            self.logger.info(f"PLinkResult collecting plink results from dir {dir_}")
        for root, dirs, files in os.walk(dir_):
            for file in files:
                if "linked_peptides.csv" in file:
                    path = os.path.join(root, file)
                    name = os.path.relpath(path, dir_).replace(os.path.sep, "/")
                    if "cross-linked" in file:
                        self._plink_result_path["CrossLink"][name] = path
                    elif "loop-linked" in file:
                        self._plink_result_path["LoopLink"][name] = path
                    elif "mono-linked" in file:
                        self._plink_result_path["MonoLink"][name] = path
                    else:
                        pass

    def add_plink_result_path(self, path, link_type, name=None) -> None:
        """Add one at one time"""
        link_type = {"cross": "CrossLink", "loop": "LoopLink", "mono": "MonoLink"}.get(
            link_type.lower(), default=link_type
        )
        if name is not None:
            self._plink_result_path[link_type][name] = path
        else:
            self._plink_result_path[link_type][path.replace(os.path.sep, "/")] = path

    def load_plink_result(self):
        if len(self._plink_result_path) == 0:
            return -1
        for link_type, plink_results in self._plink_result_path.items():
            for name, path in plink_results.items():
                if self.logger is not None:
                    self.logger.info(f"PLinkResult loading plink result: {name} - {path}")

                df = rk.flatten_two_headers_file(path, sep=",")
                if df.size == 0:
                    continue
                df["LinkType"] = link_type
                df["Source"] = name
                df["RawIndex"] = df.index.copy()
                self._plink_results[link_type][name] = df.copy()

    def stack_protein_groups(self) -> None:
        """
        Split column 'Proteins' to get all potential link pairs
        Single protein link pair is stored in new column 'SingleProteinLink'
        Rank of single protein link pair in original groups is stored in new column 'ProteinLinkRank'
        """
        pg_col = "Proteins"
        new_col = "SingleProteinLink"

        if self.logger is not None:
            self.logger.info(f"PLinkResult stacking protein groups in results")

        for link_type in list(self._plink_results.keys()):
            for name in list(self._plink_results[link_type].keys()):
                df = self._plink_results[link_type][name]

                df = df.join(
                    df[pg_col]
                    .str.strip("/")
                    .str.split("/", expand=True)
                    .stack()
                    .reset_index(level=1, drop=True)
                    .rename(new_col)
                )
                df["ProteinLinkRank"] = df.groupby(df.index).cumcount() + 1
                self._plink_results[link_type][name] = df.copy()

    def merge_collections(self, identifier_idx=None) -> None:
        """Merge all tables, w/ or w/o distance"""
        if self.logger is not None:
            self.logger.info(f"PLinkResult merging plink result collections")

        _dfs = []
        for link_type, plink_results in self._plink_results.items():
            for name, df in plink_results.items():
                if identifier_idx is not None:
                    if isinstance(identifier_idx, int):
                        if identifier_idx >= 1:
                            df["DefinedIdentifier"] = name.split("/")[-identifier_idx]
                        else:
                            raise ValueError(f"Identifier index for plink result should be a positive integer")
                _dfs.append(df)
        if len(_dfs) == 0:
            raise ValueError(f"No pLink result was loaded. Maybe all files were empty")
        else:
            self._merged_result = pd.concat(_dfs).reset_index(drop=True)

    def filter_merged_result(
        self,
        min_evalue: float = None,
        max_evalue: float = None,
        min_score: float = None,
        max_score: float = None,
        remove_gi: bool = True,
    ) -> None:
        if self.logger is not None:
            self.logger.info(
                f"PLinkResult filtering plink results {min_evalue=}, {max_evalue=}, {min_score=}, {max_score=}, {remove_gi=}"
            )

        self._merged_result_backup = self._merged_result.copy()
        if min_evalue is not None:
            self._merged_result = self._merged_result[self._merged_result["Evalue"].astype(float) > min_evalue].copy()
        if max_evalue is not None:
            self._merged_result = self._merged_result[self._merged_result["Evalue"].astype(float) < max_evalue].copy()
        if min_score is not None:
            self._merged_result = self._merged_result[self._merged_result["Score"].astype(float) > min_score].copy()
        if max_score is not None:
            self._merged_result = self._merged_result[self._merged_result["Score"].astype(float) < max_score].copy()
        if remove_gi:
            self._merged_result = self._merged_result[
                ~self._merged_result["SingleProteinLink"].str.contains("gi|", regex=False)
            ].copy()
        self._merged_result = self._merged_result.reset_index(drop=True)

    def extract_link_pair_in_merged_result(self) -> None:
        if self.logger is not None:
            self.logger.info(f"PLinkResult extracting proteins and linking positions from raw link pairs")

        new_prot_info_cols = [
            "RawProtein_1",
            "RawProtein_2",
            "RawProteinSite_1",
            "RawProteinSite_2",
            "RawProteinSiteNeedReverse",
        ]
        self._merged_result[new_prot_info_cols] = pd.DataFrame(
            self._merged_result["SingleProteinLink"].apply(extract_prot_link_info).tolist()
        )
        self._merged_result["SortedProteinLink"] = self._merged_result[new_prot_info_cols].apply(
            lambda x: combine_id_link_info(*x.values), axis=1
        )

        if self.logger is not None:
            self.logger.info(f"PLinkResult extracting peptides and linking positions from raw link pairs")

        new_pep_info_cols = [
            "RawPeptide_1",
            "RawPeptide_2",
            "RawPeptideSite_1",
            "RawPeptideSite_2",
        ]
        self._merged_result[new_pep_info_cols] = self._merged_result.apply(
            extract_pep_link_info, axis=1, result_type="expand"
        )
        self._merged_result["SortedPeptideLink"] = self._merged_result[
            [*new_pep_info_cols, "RawProteinSiteNeedReverse"]
        ].apply(lambda x: combine_id_link_info(*x.values), axis=1)

    def get_link_pairs_from_merged_result(self) -> list:
        if self.logger is not None:
            self.logger.info(f"PLinkResult getting link pairs from merged result")

        prot_links = (
            self._merged_result[
                (self._merged_result["RawProtein_2"].apply(lambda x: x is not None))
                & (~self._merged_result["RawProtein_2"].isnull())
                & (self._merged_result["RawProtein_2"] != "")
                & (self._merged_result["RawProteinSite_2"].apply(lambda x: x is not None))
                & (~self._merged_result["RawProteinSite_2"].isnull())
            ]["SortedProteinLink"]
            .dropna()
            .drop_duplicates()
            .tolist()
        )
        return prot_links

    def map_xwalk_dist_to_merged_result(
        self,
        link_to_euclidean: dict,
        link_to_sas: dict,
        prot_to_standard_map: typing.Union[dict, typing.Callable] = None,
    ):
        if self.logger is not None:
            self.logger.info(f"PLinkResult mapping xwalk calculated distances to plink results")

        if prot_to_standard_map is not None:
            if isinstance(prot_to_standard_map, dict):
                self._merged_result["StandardProtein_1"] = self._merged_result["RawProtein_1"].map(prot_to_standard_map)
                self._merged_result["StandardProtein_2"] = self._merged_result["RawProtein_2"].map(prot_to_standard_map)
            else:
                self._merged_result["StandardProtein_1"] = self._merged_result["RawProtein_1"].apply(
                    prot_to_standard_map
                )
                self._merged_result["StandardProtein_2"] = self._merged_result["RawProtein_2"].apply(
                    prot_to_standard_map
                )

            self._merged_result["SortedStandardProteinLink"] = self._merged_result[
                [
                    "StandardProtein_1",
                    "StandardProtein_2",
                    "RawProteinSite_1",
                    "RawProteinSite_2",
                    "RawProteinSiteNeedReverse",
                ]
            ].apply(lambda x: combine_id_link_info(*x.values), axis=1)

            used_dist_map_col = "SortedStandardProteinLink"

        else:
            used_dist_map_col = "SortedProteinLink"

        self._merged_result["Euclidean"] = self._merged_result[used_dist_map_col].map(link_to_euclidean)
        self._merged_result["SAS"] = self._merged_result[used_dist_map_col].map(link_to_sas)

    def write_merged_result(self, to_path: str) -> None:
        if self.logger is not None:
            self.logger.info(f"PLinkResult writing merged result to {to_path}")

        if self._merged_result is not None:
            rk.pd_df_to_file(self._merged_result, to_path, index=False)
        else:
            raise ValueError(f"pLink results have not been merged or no data defined")

    def get_merged_result(self) -> pd.DataFrame:
        return self._merged_result

    def set_merged_result(self, result: pd.DataFrame) -> None:
        self._merged_result = result.copy()

    def load_merged_result(self, path: str) -> None:
        self._merged_result = rk.pd_load_file_to_df(path)

    def write_results_from_merged_result(self, path: str) -> None:
        if self.logger is not None:
            self.logger.info(f"PLinkResult writing final result to {path}")

        df = self._merged_result.copy()
        df["I"] = df.groupby("SortedProteinLink")["Evalue"].transform(lambda x: x.astype(float).idxmin()).astype(int)
        df["Best_Evalue"] = df.apply(lambda x: df["Evalue"].iloc[x["I"]], axis=1)
        df["Score_In_Best_Evalue"] = df.apply(lambda x: df["Score"].iloc[x["I"]], axis=1)
        df["Best_Score"] = df.groupby("SortedProteinLink")["Score"].transform(
            lambda x: x.iloc[np.argmax(x.astype(float))]
        )

        with pd.ExcelWriter(path) as e:
            # Site level result
            if self.logger is not None:
                self.logger.info(f"PLinkResult writing site level result")

            site_level_result = df.copy()
            site_level_cols = [
                "SortedProteinLink",
                "SortedStandardProteinLink",
                "Protein_Type",
                "LinkType",
                "DefinedIdentifier",
                "Proteins",
                "SingleProteinLink",
                "ProteinLinkRank",
                "Source",
                "RawIndex",
                "RawProtein_1",
                "RawProtein_2",
                "StandardProtein_1",
                "StandardProtein_2",
                "RawProteinSite_1",
                "RawProteinSite_2",
                "RawProteinSiteNeedReverse",
                "Best_Evalue",
                "Score_In_Best_Evalue",
                "Best_Score",
                "SAS",
                "Euclidean",
            ]
            site_level_cols = site_level_result.columns.intersection(site_level_cols)

            site_level_result = site_level_result[site_level_cols]
            site_level_result = site_level_result.drop_duplicates(["SortedProteinLink", "Source"]).sort_values(
                ["LinkType", "SortedProteinLink", "Source"]
            )
            site_level_result.to_excel(excel_writer=e, sheet_name="Site", index=False)

            # Unique site result
            if self.logger is not None:
                self.logger.info(f"PLinkResult writing unique site level result")

            unique_site_result = site_level_result.copy()
            unique_site_level_cols = copy.deepcopy(site_level_cols)
            unique_site_level_cols = [
                _ for _ in unique_site_level_cols if _ not in ["Source", "RawIndex", "DefinedIdentifier"]
            ]
            unique_site_result = unique_site_result[unique_site_level_cols]
            unique_site_result = unique_site_result.drop_duplicates(["SortedProteinLink"]).sort_values(
                ["LinkType", "SortedProteinLink"]
            )
            unique_site_result.to_excel(excel_writer=e, sheet_name="UniqueSite", index=False)

            # Peptide level result
            if self.logger is not None:
                self.logger.info(f"PLinkResult writing peptide level result")

            pep_level_result = df.copy()
            pep_level_cols = [
                "SortedProteinLink",
                "SortedStandardProteinLink",
                "SortedPeptideLink",
                "Protein_Type",
                "LinkType",
                "DefinedIdentifier",
                "Proteins",
                "SingleProteinLink",
                "ProteinLinkRank",
                "Peptide",
                "Modifications",
                "Title",
                "Peptide_Mass",
                "Source",
                "RawIndex",
                "RawProtein_1",
                "RawProtein_2",
                "StandardProtein_1",
                "StandardProtein_2",
                "RawProteinSite_1",
                "RawProteinSite_2",
                "RawProteinSiteNeedReverse",
                "RawPeptide_1",
                "RawPeptide_2",
                "RawPeptideSite_1",
                "RawPeptideSite_2",
                "Best_Evalue",
                "Score_In_Best_Evalue",
                "Best_Score",
                "SAS",
                "Euclidean",
            ]
            pep_level_cols = pep_level_result.columns.intersection(pep_level_cols)
            pep_level_result = pep_level_result[pep_level_cols]
            pep_level_result = pep_level_result.drop_duplicates(
                ["Source", "SortedProteinLink", "SortedPeptideLink"]
            ).sort_values(["LinkType", "Source", "SortedProteinLink", "SortedPeptideLink", "Best_Evalue"])
            pep_level_result.to_excel(excel_writer=e, sheet_name="Peptide", index=False)

            # PSM level result
            if self.logger is not None:
                self.logger.info(f"PLinkResult writing PSM level result")

            (
                self._merged_result.sort_values(
                    ["LinkType", "Source", "SortedProteinLink", "SortedPeptideLink"]
                ).to_excel(excel_writer=e, sheet_name="PSM", index=False)
            )
