# main.py

from ingestion.pubmed_ingestor import fetch_pubmed_results
from utils.filters import abstract_mentions_statistics
from summarization.summarizer import summarize_articles

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    parser.add_argument("--max_results", type=int, default=50)
    args = parser.parse_args()

    print(f"🔍 Searching PubMed for: {args.query}")
    articles = fetch_pubmed_results(args.query, args.max_results)
    print(f"✅ Retrieved {len(articles)} results")

    filtered = [a for a in articles if abstract_mentions_statistics(a['abstract'])]
    print(f"📊 {len(filtered)} articles mention statistical analysis")

    summaries = summarize_articles(filtered)
    for entry in summaries:
        print(f"\n📰 {entry['title']}\n🧠 Summary: {entry['summary']}\n")

if __name__ == "__main__":
    main()

