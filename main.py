# main.py

import argparse
from ingestion.pubmed_ingestor import fetch_pubmed_results
from utils.filters import abstract_mentions_statistics
from summarization.summarizer import summarize_articles
from nlp.query_interpreter import interpret_query
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, required=True, help="Natural language search prompt")
    parser.add_argument("--max_results", type=int, default=100, help="Max number of results to fetch")
    args = parser.parse_args()

    # Step 1: Interpret user query with LLM
    print(f"🤖 Interpreting prompt: {args.prompt}\n")
    interpreted = interpret_query(args.prompt)
    try:
        parsed = json.loads(interpreted)
    except json.JSONDecodeError:
        print("❌ Failed to parse LLM output as JSON. Response was:")
        print(interpreted)
        return

    print("📄 Interpreted Query:")
    print(json.dumps(parsed, indent=2))

    pubmed_query = parsed.get("pubmed_query")
    max_results = args.max_results

    # Step 2: Fetch from PubMed
    print(f"\n🔍 Searching PubMed for: {pubmed_query}")
    articles = fetch_pubmed_results(pubmed_query, max_results)

    # Step 3: Filter for stats relevance
    filtered = [a for a in articles if abstract_mentions_statistics(a.get("abstract", ""))]
    print(f"✅ {len(filtered)} articles mention statistical analysis")

    # Step 4: Summarize
    summaries = summarize_articles(filtered)
    for idx, entry in enumerate(summaries, 1):
        print(f"\n📝 Summary #{idx}:\n{entry['summary']}")

if __name__ == "__main__":
    main()

