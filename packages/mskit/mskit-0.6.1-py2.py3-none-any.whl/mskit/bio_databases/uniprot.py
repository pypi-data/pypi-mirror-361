"""
https://www.uniprot.org/help/programmatic_access
https://www.uniprot.org/help/api

"""

species_to_general_organismid = {
    "ARATH": 3702,
    "CAEEL": 6239,
    "DROME": 7227,
    "ECOLI": 83333,
    "HUMAN": 9606,
    "MOUSE": 10090,
    "RAT": 10116,
    "YEAST": 559292,
}
species_to_general_proteomeid = {
    "ARATH": "UP000006548",
    "CAEEL": "UP000001940",
    "DROME": "UP000000803",
    "ECOLI": "UP000000625",
    "HUMAN": "UP000005640",
    "MOUSE": "UP000000589",
    "RAT": "UP000002494",
    "YEAST": "UP000002311",
}
keyword_category_to_keyword_id = {
    "Membrane": "KW-0472",
    "Transmembrane": "KW-0812",
    "GPCR": "KW-0297",
    "IonChannel": "KW-0407",
    "Transport": "KW-0813",
    "PTK": "KW-0829",
    "PSThK": "KW-0723",
    "PotassiumChannel": "KW-0631",
    "SodiumChannel": "KW-0894",
    "ChlorideChannel": "KW-0869",
    "CalciumChannel": "KW-0107",
}

tsv_fields = "accession,reviewed,id,protein_name,gene_names,organism_name,length"
extended_tsv_fields = (
    tsv_fields + ",keywordid,ft_topo_dom,ft_intramem,ft_transmem,cc_pathway,protein_families,cc_subcellular_location"
)


def get_identifier(species, organismid=None, proteomeid=None, keyword=None, date=None, file_formet=None):
    ident = f"{species}"
    if organismid is None:
        organismid = species_to_general_organismid.get(species)
    ident = f"{ident}-{organismid}"
    if proteomeid is None:
        proteomeid = species_to_general_proteomeid.get(species)
    ident = f"{ident}-{proteomeid}"
    if keyword is not None:
        if keyword.startswith("KW-"):
            pass
        else:
            keyword = keyword_category_to_keyword_id.get(keyword)
    ident = f"{ident}-{keyword}"
    if date is not None:
        ident = f"{ident}-{date}"
    if file_formet is not None:
        ident = f"{ident}.{file_formet}"
    return ident
