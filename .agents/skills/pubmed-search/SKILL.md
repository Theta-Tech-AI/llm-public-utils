---
name: pubmed-search
description: Search PubMed and display structured paper metadata. Use when the user wants literature search results with titles, authors, abstracts, DOIs, and PubMed links.
---

# PubMed Search

Search PubMed via NCBI Entrez and print structured results for the top matches.

## Bundled Script

Run `search_pubmed.py` in this directory:

```bash
python search_pubmed.py --query "your search terms here"
```

## Prerequisites

```bash
pip install biopython
```

Set `Entrez.email` in the script (or override via env) to a valid contact email — NCBI requires this for Entrez API access.

## Behavior

- Returns up to 3 results by default (`MAX_RESULTS` in the script).
- Prints title, authors, journal, year, DOI, PubMed URL, and abstract for each paper.
- Uses structured logging with emoji prefixes.

## When to Use

- Quick literature scans during research or writing tasks
- Verifying paper metadata before citing
- Gathering abstracts for summarization or critique workflows
