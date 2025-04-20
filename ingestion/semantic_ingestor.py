# ingestion/semantic_ingestor.py

import os
import json
import requests
from tqdm import tqdm

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = ",".join([
    "paperId", "title", "abstract", "authors", "year", "venue", "url",
    "citationCount", "isOpenAccess", "openAccessPdf", "externalIds", "fieldsOfStudy"
])

def search_semantic_scholar(query, max_results=20, fields_of_study=None, pub_type=None):
    headers = {
        "x-api-key": "YOUR_API_KEY_HERE",
        "User-Agent": "LiteratureReviewApp/1.0"
    }

    results = []
    offset = 0
    page_size = min(max_results, 100)  

    while len(results) < max_results:
        params = {
            "query": query,
            "limit": page_size,
            "offset": offset,
            "fields": FIELDS
        }
        if fields_of_study:
            params["fieldsOfStudy"] = fields_of_study
        if pub_type:
            params["publicationTypes"] = pub_type

        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Semantic Scholar API error: {response.status_code} - {response.text}")

        batch = response.json().get("data", [])
        if not batch:
            print("No more results found.")
            break

        results.extend(batch)
        offset += page_size

    return results[:max_results]

def parse_paper(paper):
    return {
        "paper_id": paper.get("paperId"),
        "title": paper.get("title", ""),
        "abstract": paper.get("abstract", ""),
        "authors": [author.get("name") for author in paper.get("authors", [])],
        "year": paper.get("year"),
        "venue": paper.get("venue"),
        "url": paper.get("url"),
        "citation_count": paper.get("citationCount", 0),
        "is_open_access": paper.get("isOpenAccess", False),
        "open_access_pdf": paper.get("openAccessPdf", {}).get("url"),
        "external_ids": paper.get("externalIds", {}),
        "fields_of_study": paper.get("fieldsOfStudy", [])
    }

def save_results(query, papers):
    os.makedirs("data/raw", exist_ok=True)
    filename = f"semantic_{query.replace(' ', '_')}.json"
    file_path = os.path.join("data/raw", filename)
    with open(file_path, "w") as f:
        json.dump(papers, f, indent=2)
    print(f"Saved {len(papers)} papers to {file_path}")

def run(query, max_results, field, pub_type):
    raw_results = search_semantic_scholar(
        query=query,
        max_results=max_results,
        fields_of_study=field,
        pub_type=pub_type
    )
    parsed = [parse_paper(p) for p in tqdm(raw_results)]
    save_results(query, parsed)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch Semantic Scholar papers with advanced filters")
    parser.add_argument("--query", type=str, required=True, help="Search query")
    parser.add_argument("--max_results", type=int, default=20, help="Number of papers to retrieve")
    parser.add_argument("--field", type=str, default=None, help="Field of study (e.g. Medicine, Biology)")
    parser.add_argument("--pub_type", type=str, default=None, help="Publication type (e.g. JournalArticle, Review)")

    args = parser.parse_args()
    run(args.query, args.max_results, args.field, args.pub_type)

