# query_interpreter.py

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def interpret_query(user_input):
    prompt = f"""
You are a biomedical research assistant. Your job is to convert user research prompts into structured search instructions for a PubMed-based literature review tool.

Here is the user's query:
"{user_input}"

Break it down into the following fields:
1. pubmed_query: a clean boolean query string for PubMed (e.g., "machine learning AND breast cancer")
2. field: the research domain if specified (e.g., medicine, oncology)
3. post_filter_keywords: a list of keywords to match in abstracts (e.g., ["p-value", "regression", "ANOVA"])
4. suggested_mesh_terms: MeSH terms relevant to the query (e.g., ["Breast Neoplasms", "Neural Networks (Computer)"])
5. user_intent: a 1-line summary of what the user wants to know (e.g., "summarize statistical evaluation methods")

Respond with a JSON object.
"""

    messages = [
        {"role": "system", "content": "You are a biomedical NLP assistant."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=400
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print("❌ LLM query interpretation failed:", e)
        return None

# Example usage
if __name__ == "__main__":
    query = "How many articles have used machine learning in breast cancer and what was the statistical evaluation used in them?"
    result = interpret_query(query)
    print("\n📊 Interpreted Query Output:\n", result)
