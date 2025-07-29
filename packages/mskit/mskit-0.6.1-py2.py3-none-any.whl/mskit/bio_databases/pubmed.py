"""
https://www.ncbi.nlm.nih.gov/pmc/about/userguide/
https://www.ncbi.nlm.nih.gov/pmc/tools/oa-service/
https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/

<OA>
<responseDate>2023-12-08 07:52:26</responseDate>
<request id="PMC5334499">
https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC5334499
</request>
<records returned-count="2" total-count="2">
<record id="PMC5334499" citation="World J Radiol. 2017 Feb 28; 9(2):27-33" license="CC BY-NC" retracted="no">
<link format="tgz" updated="2021-12-16 16:16:38" href="ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/8e/71/PMC5334499.tar.gz"/>
<link format="pdf" updated="2017-03-03 06:05:17" href="ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/8e/71/WJR-9-27.PMC5334499.pdf"/>
</record>
</records>
</OA>

"""


import requests


def get_pmc_id_from_doi(doi: str, return_raw_json: bool = False):
    url = f'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={doi}&format=json'
    response = requests.get(url)
    data = response.json()
    try:
        pmc_id = data['records'][0]['pmcid']
    except KeyError:
        pmc_id = None
    return pmc_id
