# summarization/summarize_pubmed.py

import os
import json
import argparse
import openai  # or any LLM client you want
from tqdm import tqdm

# ========== SETTINGS ==========
LLM_MODEL = "gpt-4-turbo"  # or your available model
CHUNK_SIZE = 3000  # characters per prompt chunk (adjust as needed)

# ========== 1. Load abstracts ==========
def load_filtered_abstracts(file_path="data/raw/pubmed_filtered.json"):
    with open(file_path, "r") as f:
        return json.load(f)

# ========== 2. Split abstracts into manageable chunks ==========
def chunk_abstracts(abstracts):
    chunks = []
    current_chunk = ""

    for entry in abstracts:
        abstract = entry.get("abstract", "")
        if not abstract:
            continue

        if len(current_chunk) + len(abstract) > CHUNK_SIZE:
            chunks.append(current_chunk)
            current_chunk = ""

        current_chunk += f"\nTitle: {entry.get('title', '')}\nAbstract: {abstract}\n"

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

# ========== 3. Summarize using LLM ==========
def summarize_chunk(chunk):
    prompt = f"""
You are a scientific assistant.

I will give you several medical journal abstracts below. Your task:
- Focus on identifying the types of **statistical analysis** discussed
- Summarize **key findings** if present
- List **methodologies** or techniques used
- Write clean, bullet-point summaries.

Abstracts:
{chunk}

Respond in well-organized markdown format.
"""
    try:
        response = openai.ChatCompletion.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful scientific assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None

# ========== 4. Save Summaries ==========
def save_summaries(summaries, out_path="data/processed/pubmed_summary.md"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        for idx, summary in enumerate(summaries, 1):
            f.write(f"## Summary Chunk {idx}\n\n")
            f.write(summary)
            f.write("\n\n")
    print(f"✅ Summaries saved to {out_path}")

# ========== 5. Main Function ==========
def run():
    abstracts = load_filtered_abstracts()
    print(f"✅ Loaded {len(abstracts)} filtered abstracts.")

    chunks = chunk_abstracts(abstracts)
    print(f"📚 Split into {len(chunks)} chunks.")

    summaries = []
    for chunk in tqdm(chunks, desc="Summarizing"):
        summary = summarize_chunk(chunk)
        if summary:
            summaries.append(summary)

    save_summaries(summaries)

# ========== 6. CLI ==========
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    run()
