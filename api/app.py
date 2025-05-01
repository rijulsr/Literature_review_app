from fastapi import FastAPI
from pydantic import BaseModel
from nlp.query_interpreter import interpret_query
from ingestion.pubmed_ingestor import fetch_pubmed_results
from summarization.summarizer import summarize_articles
import json

app = FastAPI()

class PromptReq(BaseModel):
    prompt: str
    max_results: int = 100

@app.post("/interpret")
def interpret(req: PromptReq):
    return json.loads(interpret_query(req.prompt))

@app.post("/search")
def search(req: PromptReq):
    q_struct = json.loads(interpret_query(req.prompt))
    articles = fetch_pubmed_results(q_struct["pubmed_query"], req.max_results)
    summaries = summarize_articles(articles)
    q_struct["summaries"] = summaries
    return q_struct

