### Literature Review App

This is an AI-powered tool that searches PubMed (and soon Semantic Scholar + arXiv) for medical literature and performs deep summarization using LLMs — optimized for finding statistical methods in medical research.

Features

🔎 Query PubMed for high-volume article results

🧪 Filter for studies using statistical analysis

🧠 LLM-powered summarization of relevant findings

✅ Clean architecture for expansion to more sources

## Usage
```
python main.py --query "statistical analysis in pancreatic cancer" --max_results 100
```
## Setup

1. Clone the repository

```
git clone https://github.com/YourUsername/Literature_review_app.git
cd Literature_review_app
```

2. Create a virtual environment (recommended)
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Run the app
```
python main.py --query "statistical analysis in pancreatic cancer" --max_results 100
```
# You should see:

A list of relevant PubMed articles

Summarized insights from the LLM


#Coming Soon

Semantic Scholar integration

arXiv ingestion

PDF-based summarization

