# utils/filters.py

import re

STATISTICAL_KEYWORDS = [
    "p-value", "multivariate", "regression", "ANOVA", 
    "chi-square", "logistic", "cox model", "hazard ratio",
]

def abstract_mentions_statistics(abstract):
    return any(re.search(rf"\b{kw}\b", abstract, re.IGNORECASE) for kw in STATISTICAL_KEYWORDS)

