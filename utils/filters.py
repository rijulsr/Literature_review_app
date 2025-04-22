def abstract_mentions_statistics(abstract: str) -> bool:
    """Check if an abstract mentions statistical analysis."""
    if not abstract:
        return False
        
    statistical_terms = {
        'statistical analysis',
        'statistical significance',
        'p-value',
        'confidence interval',
        'standard deviation',
        'chi-square',
        'regression',
        't-test',
        'anova',
        'correlation',
        'mean',
        'median',
        'statistical test',
        'statistically significant',
        'p < ',
        'p<',
        'p=',
        'p = ',
    }
    
    abstract = abstract.lower()
    return any(term in abstract for term in statistical_terms)
