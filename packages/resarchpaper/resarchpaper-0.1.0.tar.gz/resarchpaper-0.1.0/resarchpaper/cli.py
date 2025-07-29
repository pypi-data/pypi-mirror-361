import typer
from typing import Optional
from resarchpaper.pubmed_fetcher import fetch_pubmed_ids, fetch_paper_details
from resarchpaper.pubmed_processing import process_articles
from resarchpaper.csvwriter import write_csv

app = typer.Typer()

@app.command()
def get_papers_list(
    query: str = typer.Argument(..., help="PubMed search query"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="CSV filename (optional)"),
    email: str = typer.Option(..., "--email", help="Email for Entrez API (required)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="NCBI API key (optional)"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Print debug information"),
):
    """
    Fetch PubMed papers matching QUERY,
    filter authors affiliated with pharma/biotech,
    and save results to CSV or print to console.
    """

    if debug:
        typer.echo(f"[DEBUG] Searching for: {query}")

    # Fetch PubMed IDs matching the query
    pmids = fetch_pubmed_ids(query, retmax=20, email=email, api_key=api_key)
    if debug:
        typer.echo(f"[DEBUG] Found PMIDs: {pmids}")

    if not pmids:
        typer.echo("No PubMed IDs found for this query.")
        raise typer.Exit(code=1)

    # Fetch detailed article info for those IDs
    articles = fetch_paper_details(pmids, email=email, api_key=api_key)
    if debug:
        typer.echo(f"[DEBUG] Retrieved {len(articles)} article(s).")

    # Process articles to filter for non-academic authors
    rows = process_articles(articles)
    if debug:
        typer.echo(f"[DEBUG] {len(rows)} article(s) matched non-academic criteria.")

    # Write results to CSV or print if no file specified
    write_csv(rows, file)

if __name__ == "__main__":
    app()
