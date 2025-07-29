from typing import List, Dict, Any


def extract_author_info(article: Dict[str, Any]) -> List[Dict[str, Any]]:
    authors = article["MedlineCitation"]["Article"].get("AuthorList", [])
    author_data = []
    for auth in authors:
        name_parts = []
        if "LastName" in auth:
            name_parts.append(auth["LastName"])
        if "ForeName" in auth:
            name_parts.append(auth["ForeName"])
        name = " ".join(name_parts).strip()

        affiliations = []
        if "AffiliationInfo" in auth:
            affiliations = [aff["Affiliation"] for aff in auth["AffiliationInfo"] if "Affiliation" in aff]

        # Attempt to find email in affiliations or somewhere else
        email = None
        for aff in affiliations:
            if "@" in aff:
                email = aff
                break

        author_data.append({
            "name": name,
            "affiliations": affiliations,
            "email": email
        })
    return author_data


# Heuristic keywords for pharma/biotech companies
NON_ACAD_KEYWORDS = [
    "pharma", "biotech", "inc", "ltd", "llc", "gmbh", "ag", "corporation", "company", "laboratories", "lab"
]


def is_non_academic(affiliations: List[str]) -> bool:
    for aff in affiliations:
        aff_lower = aff.lower()
        if any(keyword in aff_lower for keyword in NON_ACAD_KEYWORDS):
            return True
        # Heuristic: no "university", "college", "institute" in affiliation means likely non-academic
        if not any(academic_word in aff_lower for academic_word in
                   ["university", "college", "institute", "hospital", "school"]):
            # If no academic keywords and has text, consider non-academic
            if aff.strip():
                return True
    return False


def process_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    rows = []
    for art in articles:
        citation = art["MedlineCitation"]
        pmid = citation["PMID"]
        article = citation["Article"]

        title = article.get("ArticleTitle", "")
        pub_date = ""
        pub_date_info = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        if "Year" in pub_date_info:
            pub_date = pub_date_info["Year"]
            if "Month" in pub_date_info:
                pub_date += f"-{pub_date_info['Month']}"
            if "Day" in pub_date_info:
                pub_date += f"-{pub_date_info['Day']}"

        authors = extract_author_info(art)

        non_acad_authors = []
        companies = set()
        corresponding_email = ""

        # Find non-academic authors and their affiliations
        for auth in authors:
            if is_non_academic(auth["affiliations"]):
                non_acad_authors.append(auth["name"])
                # Add affiliations with pharma keywords only
                for aff in auth["affiliations"]:
                    aff_lower = aff.lower()
                    if any(keyword in aff_lower for keyword in NON_ACAD_KEYWORDS):
                        companies.add(aff)

            # Capture corresponding author email if present (heuristic: first author with email)
            if not corresponding_email and auth.get("email"):
                corresponding_email = auth["email"]

        if non_acad_authors:
            rows.append({
                "PubmedID": pmid,
                "Title": title,
                "Publication Date": pub_date,
                "Non-academic Author(s)": "; ".join(non_acad_authors),
                "Company Affiliation(s)": "; ".join(companies),
                "Corresponding Author Email": corresponding_email
            })
    return rows
