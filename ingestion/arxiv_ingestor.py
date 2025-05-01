# ingestion/arxiv_ingestor.py

import requests
import xml.etree.ElementTree as ET
import argparse
import json
import os
from urllib.parse import quote

# Namespaces for parsing arXiv Atom feed
NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}

ARXIV_API_URL = 'http://export.arxiv.org/api/query'

# === 1. Search arXiv and fetch entries ===
def search_arxiv(query, max_results=100, categories=None):
    # Build the search_query parameter
    terms = []
    # all:{query}
    terms.append(f'all:{quote(query)}')
    # Optional category filters, e.g. cs.LG, q-bio.BM
    if categories:
        for cat in categories:
            terms.append(f'cat:{cat}')
    search_query = '+AND+'.join(terms)

    params = {
        'search_query': search_query,
        'start': 0,
        'max_results': max_results
    }
    response = requests.get(ARXIV_API_URL, params=params)
    response.raise_for_status()
    return response.text

# === 2. Parse Atom XML into Python objects ===
def parse_arxiv_feed(xml_text):
    root = ET.fromstring(xml_text)
    entries = []
    for entry in root.findall('atom:entry', NS):
        arxiv_id = entry.find('atom:id', NS).text
        title = entry.find('atom:title', NS).text.strip()
        summary = entry.find('atom:summary', NS).text.strip()
        published = entry.find('atom:published', NS).text
        # Authors
        authors = []
        for author in entry.findall('atom:author', NS):
            name = author.find('atom:name', NS).text
            authors.append(name)
        # Primary category
        primary = entry.find('arxiv:primary_category', NS).attrib.get('term')
        # All categories
        cats = [c.attrib.get('term') for c in entry.findall('atom:category', NS)]
        # PDF link
        pdf_url = ''
        for link in entry.findall('atom:link', NS):
            if link.attrib.get('title') == 'pdf':
                pdf_url = link.attrib.get('href')
                break
        entries.append({
            'id': arxiv_id,
            'title': title,
            'summary': summary,
            'published': published,
            'authors': authors,
            'primary_category': primary,
            'categories': cats,
            'pdf_url': pdf_url
        })
    return entries

# === 3. Save results to JSON ===
def save_results(query, entries):
    os.makedirs('data/raw', exist_ok=True)
    filename = f"arxiv_{query.replace(' ', '_')}.json"
    path = os.path.join('data/raw', filename)
    with open(path, 'w') as f:
        json.dump(entries, f, indent=2)
    print(f"✅ Saved {len(entries)} entries to {path}")

# === 4. Main CLI ===
def run(query, max_results, categories):
    print(f"🔍 Querying arXiv for: {query} (max {max_results})")
    xml_text = search_arxiv(query, max_results, categories)
    entries = parse_arxiv_feed(xml_text)
    save_results(query, entries)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch papers from arXiv')
    parser.add_argument('--query', type=str, required=True, help='Search query for arXiv')
    parser.add_argument('--max_results', type=int, default=100, help='Max number of results')
    parser.add_argument('--categories', type=str, default=None,
                        help='Comma-separated list of arXiv categories (e.g., cs.LG, q-bio.BM)')
    args = parser.parse_args()

    cats = args.categories.split(',') if args.categories else None
    run(args.query, args.max_results, cats)

