# Research Paper Fetcher

A Python tool to fetch research papers from PubMed based on a user query, filtering for papers with authors affiliated with pharmaceutical or biotech companies, and exporting the results to CSV.

## Features

- Uses PubMed API with full query syntax support
- Filters for non-academic authors (pharma/biotech affiliations)
- Command-line interface with options for debug info, output file, email & API key
- Outputs data including PubMed ID, title, publication date, author affiliations, and corresponding author email
- Written in typed Python with Poetry for dependency management

## Installation

Make sure you have Python 3.8+ installed.

1. **Clone the repository:**
git clone https://github.com/ritujadik/ResarchPaperProject.git
cd ResarchPaperProject

2. **Install dependencies with Poetry:**
 poetry install
3. **Usage**
 poetry shell
 Run the CLI tool:
 "python -m resarchpaper "cancer therapy" --email your_email@example.com --file output.csv --debug"
4.**Command-line Options**
--email (required): Your email for NCBI Entrez API.
--api-key (optional): Your NCBI API key for higher rate limits.
--file or -f: CSV output filename (prints to console if not specified).
--debug or -d: Prints debug information during execution.
--help or -h: Show help message.
5.**Development**
The project is modular:
pubmed_fetcher.py handles PubMed API calls
pubmed_processing.py processes and filters articles
csvwriter.py exports data to CSV
cli.py handles command-line interface
6.**External Libraries & Tools**
Biopython for Entrez API interaction
Typer for CLI
Poetry for dependency management
