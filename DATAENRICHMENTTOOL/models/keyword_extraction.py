"""
Keyword extraction module for product data.

This module provides functions for extracting keywords from product data
using various NLP techniques, focusing on scikit-learn based approaches
since we had to use lightweight alternatives due to disk space constraints.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from src.utils.text_preprocessing import preprocess_text

def extract_keywords_tfidf(text, max_keywords=10, ngram_range=(1, 2)):
    """
    Extract keywords using TF-IDF.
    
    Args:
        text (str): Input text
        max_keywords (int): Maximum number of keywords to extract
        ngram_range (tuple): Range of n-grams to consider
        
    Returns:
        list: List of (keyword, score) tuples
    """
    if not isinstance(text, str) or not text:
        return []
    
    # Preprocess text
    processed_text = preprocess_text(text)
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=ngram_range,
        max_features=100,
        stop_words='english'
    )
    
    try:
        # Fit and transform text
        tfidf_matrix = vectorizer.fit_transform([processed_text])
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Get TF-IDF scores
        tfidf_scores = tfidf_matrix.toarray()[0]
        
        # Create keyword-score pairs
        keyword_scores = [(feature_names[i], tfidf_scores[i]) for i in range(len(feature_names))]
        
        # Sort by score and take top keywords
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        top_keywords = keyword_scores[:max_keywords]
        
        return top_keywords
    except Exception as e:
        print(f"Error in TF-IDF keyword extraction: {e}")
        return []

def extract_keywords_lda(text, max_keywords=10, ngram_range=(1, 2), num_topics=1):
    """
    Extract keywords using Latent Dirichlet Allocation (LDA).
    
    Args:
        text (str): Input text
        max_keywords (int): Maximum number of keywords to extract
        ngram_range (tuple): Range of n-grams to consider
        num_topics (int): Number of topics for LDA
        
    Returns:
        list: List of (keyword, score) tuples
    """
    if not isinstance(text, str) or not text:
        return []
    
    # Preprocess text
    processed_text = preprocess_text(text)
    
    # Create Count vectorizer
    vectorizer = CountVectorizer(
        ngram_range=ngram_range,
        max_features=100,
        stop_words='english'
    )
    
    try:
        # Fit and transform text
        count_matrix = vectorizer.fit_transform([processed_text])
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Create LDA model
        lda = LatentDirichletAllocation(
            n_components=num_topics,
            random_state=42,
            max_iter=10
        )
        
        # Fit LDA model
        lda.fit(count_matrix)
        
        # Get keywords for each topic
        keywords = []
        for topic_idx, topic in enumerate(lda.components_):
            # Sort words by importance
            sorted_indices = np.argsort(topic)[::-1]
            top_indices = sorted_indices[:max_keywords]
            
            # Get keywords and scores
            for i in top_indices:
                keywords.append((feature_names[i], topic[i]))
        
        # Sort by score and take top keywords
        keywords.sort(key=lambda x: x[1], reverse=True)
        top_keywords = keywords[:max_keywords]
        
        return top_keywords
    except Exception as e:
        print(f"Error in LDA keyword extraction: {e}")
        return []

def extract_keywords_from_product(product_data, max_keywords=15):
    """
    Extract keywords from product data, focusing on title, description, and features.
    
    Args:
        product_data (dict): Product data dictionary
        max_keywords (int): Maximum number of keywords to extract
        
    Returns:
        dict: Dictionary with extracted keywords for each field and combined
    """
    result = {
        'title_keywords': [],
        'description_keywords': [],
        'features_keywords': [],
        'combined_keywords': []
    }
    
    # Extract keywords from title
    if 'title' in product_data and product_data['title']:
        result['title_keywords'] = extract_keywords_tfidf(
            product_data['title'],
            max_keywords=max_keywords // 3
        )
    
    # Extract keywords from description
    if 'description' in product_data and product_data['description']:
        result['description_keywords'] = extract_keywords_tfidf(
            product_data['description'],
            max_keywords=max_keywords // 3
        )
    
    # Extract keywords from features/specifications
    features_text = ""
    if 'features' in product_data and product_data['features']:
        features_text = product_data['features']
    elif 'specifications' in product_data and product_data['specifications']:
        features_text = product_data['specifications']
    
    if features_text:
        result['features_keywords'] = extract_keywords_tfidf(
            features_text,
            max_keywords=max_keywords // 3
        )
    
    # Combine all text for overall keyword extraction
    combined_text = " ".join([
        product_data.get('title', ''),
        product_data.get('description', ''),
        features_text
    ])
    
    # Use LDA for combined text to get different perspective
    result['combined_keywords'] = extract_keywords_lda(
        combined_text,
        max_keywords=max_keywords
    )
    
    return result

def get_top_keywords(keyword_dict, max_keywords=10):
    """
    Get top keywords from all extracted keywords.
    
    Args:
        keyword_dict (dict): Dictionary with extracted keywords
        max_keywords (int): Maximum number of keywords to return
        
    Returns:
        list: List of top keywords
    """
    # Collect all keywords
    all_keywords = []
    
    # Add keywords from each category with weights
    for key, keywords in keyword_dict.items():
        weight = 2.0 if key == 'title_keywords' else 1.0
        for keyword, score in keywords:
            all_keywords.append((keyword, score * weight))
    
    # Create a dictionary to combine scores for duplicate keywords
    keyword_scores = {}
    for keyword, score in all_keywords:
        if keyword in keyword_scores:
            keyword_scores[keyword] += score
        else:
            keyword_scores[keyword] = score
    
    # Convert back to list and sort
    combined_keywords = [(k, v) for k, v in keyword_scores.items()]
    combined_keywords.sort(key=lambda x: x[1], reverse=True)
    
    # Return top keywords
    return combined_keywords[:max_keywords]
