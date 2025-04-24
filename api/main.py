from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.pubmed_ingestor import search_pubmed, fetch_details, mentions_statistics

app = FastAPI(title="Literature Review API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    max_results: int = 20
    filter_stats: bool = True

class Article(BaseModel):
    title: str
    abstract: str
    authors: List[str]
    journal: str = ""
    pubdate: str = ""
    pmid: str
    summary: Optional[str] = None

@app.post("/api/search", response_model=List[Article])
async def search_literature(request: SearchRequest):
    # Search PubMed
    ids = search_pubmed(request.query, request.max_results)
    if not ids:
        return []
    
    # Fetch article details
    articles = fetch_details(ids)
    
    # Filter for statistical analysis if requested
    if request.filter_stats:
        articles = [a for a in articles if mentions_statistics(a.get("abstract", ""))]
    
    # Skip summarization for now
    for article in articles:
        article["summary"] = "Summarization temporarily disabled"
    
    return articles

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)