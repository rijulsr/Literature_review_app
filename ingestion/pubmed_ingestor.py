# ingestion/pubmed_ingestor.py

import requests
import argparse
import time
import json
import os
import re
from tqdm import tqdm

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# === 1. Search PubMed for PMIDs ===
def search_pubmed(query, max_results=100):
    pmids = []
    retstart = 0
    retmax = 100  # fetch 100 at a time

    headers = {"Accept": "application/json"}

    while len(pmids) < max_results:
        params = {
            "db": "pubmed",
            "term": query,
            "retstart": retstart,
            "retmax": min(retmax, max_results - len(pmids)),
            "retmode": "json"
        }
        response = requests.get(f"{BASE_URL}/esearch.fcgi", params=params)
        response.raise_for_status()
        data = response.json()
        ids = data["esearchresult"]["idlist"]
        if not ids:
            break
        pmids.extend(ids)
        retstart += retmax
        time.sleep(0.5)  # be nice to NCBI
    return pmids

# === 2. Fetch Metadata for PMIDs ===
def fetch_details(pmids):
    BATCH_SIZE = 50
    all_results = []

    for i in tqdm(range(0, len(pmids), BATCH_SIZE), desc="Fetching abstracts"):
        batch = pmids[i:i + BATCH_SIZE]
        params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "json",
            "rettype": "abstract"
        }
        response = requests.get(f"{BASE_URL}/esummary.fcgi", params=params)
        response.raise_for_status()
        summaries = response.json()["result"]

        # use efetch to get full abstracts
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "xml"
        }
        fetch_response = requests.get(f"{BASE_URL}/efetch.fcgi", params=fetch_params)
        fetch_response.raise_for_status()
        xml_data = fetch_response.text

        for pid in batch:
            summary = summaries.get(pid, {})
            title = summary.get("title", "")
            journal = summary.get("fulljournalname", "")
            pubdate = summary.get("pubdate", "")
            authors = summary.get("authors", [])
            author_names = [a['name'] for a in authors if 'name' in a]
            abstract = extract_abstract_from_xml(xml_data, pid)

            all_results.append({
                "pmid": pid,
                "title": title,
                "journal": journal,
                "pubdate": pubdate,
                "authors": author_names,
                "abstract": abstract,
            })
        time.sleep(0.5)
    return all_results

# === 3. Extract Abstracts from efetch XML ===
def extract_abstract_from_xml(xml_text, pmid):
    pattern = re.compile(rf"<ArticleId IdType=\"pubmed\">{pmid}</ArticleId>.*?<Abstract>(.*?)</Abstract>", re.DOTALL)
    match = pattern.search(xml_text)
    if match:
        raw = match.group(1)
        clean = re.sub(r"<.*?>", "", raw)
        return clean.strip()
    return ""

# === 4. Regex Filter: Does Abstract Mention Stats? ===
def mentions_statistics(text):
    if not text:
        return False
    pattern = re.compile(r"(p-?value|regression|anova|odds ratio|confidence interval|multivariate|statistical significance)", re.I)
    return bool(pattern.search(text))

# === 5. Main Function ===
# === NEW: Get Total Available Results ===
def get_total_result_count(query):
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "rettype": "count"
    }
    response = requests.get(f"{BASE_URL}/esearch.fcgi", params=params)
    response.raise_for_status()
    data = response.json()
    return int(data["esearchresult"]["count"])

# === Updated Main Function ===
def run(query, max_results):
    if max_results == -1:
        print(f"🔍 Getting total available results for: {query}")
        max_results = get_total_result_count(query)
        print(f"✅ Total matching articles: {max_results}")

    print(f"🔎 Searching PubMed for: {query}")
    pmids = search_pubmed(query, max_results=max_results)
    print(f"✅ Retrieved {len(pmids)} PMIDs")

    results = fetch_details(pmids)
    print(f"🧠 Filtering for statistical analysis mentions...")
    filtered = [r for r in results if mentions_statistics(r["abstract"])]

    print(f"📄 {len(filtered)} results mention statistical analysis")

    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/pubmed_filtered.json", "w") as f:
        json.dump(filtered, f, indent=2)

    print("✅ Done. Filtered results saved to data/raw/pubmed_filtered.json")

# === Updated CLI ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Search query for PubMed")
    parser.add_argument(
        "--max_results", 
        type=int, 
        default=100, 
        help="Number of articles to retrieve (use -1 for all available)"
    )
    args = parser.parse_args()

    run(args.query, args.max_results)


