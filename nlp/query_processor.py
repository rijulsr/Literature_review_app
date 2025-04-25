from typing import Dict, List
import openai
import os
from pydantic import BaseModel

class QueryAnalysis(BaseModel):
    keywords: List[str]
    pubmed_queries: List[str]
    mesh_terms: List[str]
    search_strategy: str

class QueryProcessor:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        openai.api_key = self.api_key

    def analyze_query(self, user_query: str) -> QueryAnalysis:
        """Analyze the user's natural language query using GPT to extract structured search components."""
        
        system_prompt = """You are a medical research assistant helping to analyze search queries.
        For the given query, provide:
        1. Key search terms
        2. 3 optimized PubMed search queries (using proper syntax with AND, OR, etc.)
        3. Relevant MeSH terms
        4. A brief search strategy explanation
        Format the response as a JSON object with keys: keywords, pubmed_queries, mesh_terms, and search_strategy"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7
            )
            
            # Parse the response into our QueryAnalysis model
            result = response.choices[0].message.content
            return QueryAnalysis.parse_raw(result)
            
        except Exception as e:
            raise Exception(f"Error analyzing query: {str(e)}")

    def refine_pubmed_query(self, base_query: str, feedback: str) -> str:
        """Refine a PubMed query based on user feedback."""
        
        system_prompt = """You are a PubMed search expert. Given a base query and user feedback,
        provide an improved PubMed search query that addresses the feedback while maintaining proper syntax."""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Base Query: {base_query}\nFeedback: {feedback}"}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error refining query: {str(e)}")
