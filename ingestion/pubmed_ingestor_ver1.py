# ingestion/pubmed_ingestor.py

from Bio import Entrez
import json
import os
from tqdm import tqdm

Entrez.email = "your_email@example.com"  # Replace with your email for Entrez

def search_pubmed(query, max_results=20):
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    return record["IdList"]

def fetch_details(id_list):
    ids = ",".join(id_list)
    handle = Entrez.efetch(db="pubmed", id=ids, rettype="medline", retmode="xml")
    records = Entrez.read(handle)
    return records["PubmedArticle"]

def parse_article(article):
    try:
        article_data = article["MedlineCitation"]["Article"]
        return {
            "title": article_data.get("ArticleTitle", ""),
            "abstract": article_data.get("Abstract", {}).get("AbstractText", [""])[0],
            "authors": [
                f"{a.get('ForeName', '')} {a.get('LastName', '')}".strip()
                for a in article_data.get("AuthorList", [])
                if a.get("LastName")
            ],
            "journal": article_data.get("Journal", {}).get("Title", ""),
            "year": article_data.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {}).get("Year", ""),
            "pubmed_id": article["MedlineCitation"]["PMID"],
        }
    except Exception as e:
        print(f"Error parsing article: {e}")
        return {}

def save_results(query, articles):
    os.makedirs("data/raw", exist_ok=True)
    file_path = f"data/raw/pubmed_{query.replace(' ', '_')}.json"
    with open(file_path, "w") as f:
        json.dump(articles, f, indent=2)
    print(f"Saved {len(articles)} articles to {file_path}")

def run(query):
    ids = search_pubmed(query)
    print(f"Found {len(ids)} papers for query: {query}")
    if not ids:
        return

    raw_articles = fetch_details(ids)
    parsed = [parse_article(a) for a in tqdm(raw_articles)]
    parsed = [a for a in parsed if a]  # remove failed parses
    save_results(query, parsed)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch PubMed papers")
    parser.add_argument("--query", type=str, required=True, help="Search query")
    parser.add_argument("--max_results", type=int, default=20, help="Number of results")

    args = parser.parse_args()
    run(args.query)

