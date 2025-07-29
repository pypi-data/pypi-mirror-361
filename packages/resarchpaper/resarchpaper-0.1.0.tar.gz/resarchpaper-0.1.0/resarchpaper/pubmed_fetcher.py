from Bio import Entrez
from typing import List, Optional
from Bio.Entrez import HTTPError

def fetch_pubmed_ids(
    query: str,
    retmax: int = 20,
    email: Optional[str] = None,
    api_key: Optional[str] = None
) -> List[str]:
    if email:
        Entrez.email = email
    if api_key:
        Entrez.api_key = api_key

    try:
        with Entrez.esearch(db="pubmed", term=query, retmax=retmax) as handle:
            results = Entrez.read(handle)
            return results.get("IdList", [])
    except HTTPError as e:
        print(f"Failed to fetch PubMed IDs: {e}")
        return []

def fetch_paper_details(
    pmids: List[str],
    email: Optional[str] = None,
    api_key: Optional[str] = None
) -> List[dict]:
    if email:
        Entrez.email = email
    if api_key:
        Entrez.api_key = api_key

    if not pmids:
        return []

    try:
        with Entrez.efetch(
            db="pubmed",
            id=pmids,
            rettype="medline",
            retmode="xml"
        ) as handle:
            articles = Entrez.read(handle)
            return articles.get("PubmedArticle", [])
    except HTTPError as e:
        print(f"Failed to fetch paper details: {e}")
        return []
