"""
Data processor module for loading, processing, and enriching product data.

This module provides functions for loading data from various formats,
enriching product data with NLP-powered keyword extraction, and
exporting data to CSV files.
"""

import os
import json
import csv
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import re
import string
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Pre-download NLTK resources to a local directory to avoid download errors
NLTK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'nltk_data')
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
nltk.data.path.insert(0, NLTK_DATA_DIR)

# Define custom stopwords to use if NLTK resources are not available
CUSTOM_STOPWORDS = {
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
    'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
    'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
    'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
    'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
}

# Try to safely download NLTK resources without causing errors
try:
    nltk.download('punkt', download_dir=NLTK_DATA_DIR, quiet=True)
    nltk.download('stopwords', download_dir=NLTK_DATA_DIR, quiet=True)
    nltk.download('wordnet', download_dir=NLTK_DATA_DIR, quiet=True)
    
    # Initialize NLTK components
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    
    # Get stopwords
    try:
        stop_words = set(stopwords.words('english'))
    except:
        stop_words = CUSTOM_STOPWORDS
    
    # Initialize lemmatizer
    try:
        lemmatizer = WordNetLemmatizer()
    except:
        lemmatizer = None
    
    # Define tokenize function
    def tokenize_text(text):
        try:
            return word_tokenize(text)
        except:
            return text.split()
    
    # Define lemmatize function
    def lemmatize_word(word):
        if lemmatizer:
            return lemmatizer.lemmatize(word)
        else:
            # Simple lemmatization fallback
            if word.endswith('s') and len(word) > 3:
                return word[:-1]
            if word.endswith('ing') and len(word) > 5:
                return word[:-3]
            if word.endswith('ed') and len(word) > 4:
                return word[:-2]
            return word
            
except Exception as e:
    print(f"NLTK initialization warning: {e}")
    print("Using custom text processing functions instead.")
    
    # Use custom implementations as fallback
    stop_words = CUSTOM_STOPWORDS
    
    # Custom tokenizer function
    def tokenize_text(text):
        # Remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        # Split on whitespace
        return text.split()
    
    # Custom lemmatizer function
    def lemmatize_word(word):
        # Handle plurals ending in 's'
        if word.endswith('s') and len(word) > 3:
            word = word[:-1]
        
        # Handle common verb endings
        if word.endswith('ing') and len(word) > 5:
            word = word[:-3]
        elif word.endswith('ed') and len(word) > 4:
            word = word[:-2]
        
        return word

def load_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Load data from a file (CSV or JSON).
    
    Args:
        file_path (str): Path to the data file
        
    Returns:
        list: List of product dictionaries
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine file type from extension
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.csv':
        # Load CSV file
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    
    elif file_ext == '.json':
        # Load JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle both list and dictionary formats
        if isinstance(data, list):
            return data
        else:
            return [data]
    
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

def preprocess_text(text: str) -> str:
    """
    Preprocess text for keyword extraction.
    
    Args:
        text (str): Text to preprocess
        
    Returns:
        str: Preprocessed text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize
    tokens = tokenize_text(text)
    
    # Remove stopwords and lemmatize
    tokens = [lemmatize_word(token) for token in tokens if token not in stop_words]
    
    # Join tokens back into a string
    return ' '.join(tokens)

def extract_keywords_tfidf(text: str, max_keywords: int = 10, min_keyword_length: int = 4) -> List[Dict[str, float]]:
    """
    Extract keywords from text using TF-IDF.
    
    Args:
        text (str): Text to extract keywords from
        max_keywords (int, optional): Maximum number of keywords to extract
        min_keyword_length (int, optional): Minimum keyword length
        
    Returns:
        list: List of dictionaries with keywords and relevance scores
    """
    if not text:
        return []
    
    # Preprocess text
    preprocessed_text = preprocess_text(text)
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=max_keywords * 2,  # Extract more features than needed, then filter
        ngram_range=(1, 2),  # Consider both unigrams and bigrams
        min_df=1
    )
    
    try:
        # Fit and transform text
        tfidf_matrix = vectorizer.fit_transform([preprocessed_text])
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Get TF-IDF scores
        tfidf_scores = tfidf_matrix.toarray()[0]
        
        # Create list of (keyword, score) tuples
        keyword_scores = [(feature_names[i], tfidf_scores[i]) for i in range(len(feature_names))]
        
        # Filter by keyword length and sort by score
        keyword_scores = [(kw, score) for kw, score in keyword_scores if len(kw) >= min_keyword_length]
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top keywords
        return [{'keyword': kw, 'score': float(score)} for kw, score in keyword_scores[:max_keywords]]
    
    except Exception as e:
        print(f"Error extracting keywords with TF-IDF: {e}")
        return []

def extract_keywords_lda(text: str, max_keywords: int = 10, min_keyword_length: int = 4) -> List[Dict[str, float]]:
    """
    Extract keywords from text using Latent Dirichlet Allocation (LDA).
    
    Args:
        text (str): Text to extract keywords from
        max_keywords (int, optional): Maximum number of keywords to extract
        min_keyword_length (int, optional): Minimum keyword length
        
    Returns:
        list: List of dictionaries with keywords and relevance scores
    """
    if not text:
        return []
    
    # Preprocess text
    preprocessed_text = preprocess_text(text)
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=100,  # Use more features for LDA
        ngram_range=(1, 2),  # Consider both unigrams and bigrams
        min_df=1
    )
    
    try:
        # Fit and transform text
        tfidf_matrix = vectorizer.fit_transform([preprocessed_text])
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Create LDA model
        lda = LatentDirichletAllocation(
            n_components=1,  # Assume one topic for short texts
            random_state=42
        )
        
        # Fit LDA model
        lda.fit(tfidf_matrix)
        
        # Get topic-word distribution
        topic_word_dist = lda.components_[0]
        
        # Create list of (keyword, score) tuples
        keyword_scores = [(feature_names[i], topic_word_dist[i]) for i in range(len(feature_names))]
        
        # Filter by keyword length and sort by score
        keyword_scores = [(kw, score) for kw, score in keyword_scores if len(kw) >= min_keyword_length]
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top keywords
        return [{'keyword': kw, 'score': float(score)} for kw, score in keyword_scores[:max_keywords]]
    
    except Exception as e:
        print(f"Error extracting keywords with LDA: {e}")
        return []

def extract_keywords(text: str, max_keywords: int = 10, min_keyword_length: int = 4) -> List[Dict[str, float]]:
    """
    Extract keywords from text using multiple methods and combine results.
    
    Args:
        text (str): Text to extract keywords from
        max_keywords (int, optional): Maximum number of keywords to extract
        min_keyword_length (int, optional): Minimum keyword length
        
    Returns:
        list: List of dictionaries with keywords and relevance scores
    """
    if not text:
        return []
    
    # Extract keywords using TF-IDF
    tfidf_keywords = extract_keywords_tfidf(text, max_keywords, min_keyword_length)
    
    # Extract keywords using LDA
    lda_keywords = extract_keywords_lda(text, max_keywords, min_keyword_length)
    
    # Combine results
    keyword_dict = {}
    
    # Add TF-IDF keywords
    for kw in tfidf_keywords:
        keyword_dict[kw['keyword']] = kw['score']
    
    # Add LDA keywords with weight
    for kw in lda_keywords:
        if kw['keyword'] in keyword_dict:
            # If keyword already exists, take the higher score
            keyword_dict[kw['keyword']] = max(keyword_dict[kw['keyword']], kw['score'] * 0.8)
        else:
            # Otherwise, add with weight
            keyword_dict[kw['keyword']] = kw['score'] * 0.8
    
    # Convert back to list and sort
    combined_keywords = [{'keyword': kw, 'score': score} for kw, score in keyword_dict.items()]
    combined_keywords.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top keywords
    return combined_keywords[:max_keywords]

def calculate_relevance_score(product: Dict[str, Any], keywords: List[Dict[str, float]]) -> float:
    """
    Calculate relevance score for a product based on extracted keywords.
    
    Args:
        product (dict): Product dictionary
        keywords (list): List of keyword dictionaries
        
    Returns:
        float: Relevance score
    """
    if not keywords:
        return 0.0
    
    # Calculate base score as average of keyword scores
    base_score = sum(kw['score'] for kw in keywords) / len(keywords)
    
    # Apply modifiers based on product attributes
    modifiers = 1.0
    
    # Modifier for product title length
    title = product.get('title', '')
    if title:
        title_length = len(title.split())
        if title_length > 10:
            modifiers *= 1.2  # Longer titles often have more information
        elif title_length < 3:
            modifiers *= 0.8  # Very short titles may lack information
    
    # Modifier for description length
    description = product.get('description', '')
    if description:
        desc_length = len(description.split())
        if desc_length > 100:
            modifiers *= 1.1  # Longer descriptions often have more information
        elif desc_length < 20:
            modifiers *= 0.9  # Very short descriptions may lack information
    
    # Modifier for price (if available)
    price = product.get('price', 0)
    if price > 0:
        if price > 100:
            modifiers *= 1.05  # Higher-priced items often have more detailed information
    
    # Calculate final score
    return base_score * modifiers

def enrich_product_data(products: List[Dict[str, Any]], max_keywords: int = 10, min_keyword_length: int = 4) -> List[Dict[str, Any]]:
    """
    Enrich product data with NLP-powered keyword extraction.
    
    Args:
        products (list): List of product dictionaries
        max_keywords (int, optional): Maximum number of keywords to extract per product
        min_keyword_length (int, optional): Minimum keyword length
        
    Returns:
        list: List of enriched product dictionaries
    """
    enriched_products = []
    
    for product in products:
        # Create a copy of the product
        enriched_product = product.copy()
        
        # Extract text from relevant fields
        title = product.get('title', '')
        description = product.get('description', '')
        features = product.get('features', '')
        
        # Combine text for keyword extraction
        combined_text = f"{title}\n{description}\n{features}"
        
        # Extract keywords
        keywords = extract_keywords(combined_text, max_keywords, min_keyword_length)
        
        # Calculate relevance score
        relevance_score = calculate_relevance_score(product, keywords)
        
        # Add enriched data
        enriched_product['keywords'] = [kw['keyword'] for kw in keywords]
        enriched_product['keyword_scores'] = keywords
        enriched_product['relevance_score'] = relevance_score
        
        enriched_products.append(enriched_product)
    
    return enriched_products

def generate_metadata(enriched_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate search-friendly metadata from enriched products.
    
    Args:
        enriched_products (list): List of enriched product dictionaries
        
    Returns:
        list: List of metadata dictionaries
    """
    metadata = []
    
    for product in enriched_products:
        # Extract product identifiers
        product_id = product.get('id', '')
        asin = product.get('asin', '')
        sku = product.get('sku', '')
        upc = product.get('upc', '')
        
        # Extract keywords and scores
        keywords = product.get('keywords', [])
        keyword_scores = product.get('keyword_scores', [])
        
        # Create metadata entry
        meta_entry = {
            'product_id': product_id,
            'asin': asin,
            'sku': sku,
            'upc': upc,
            'title': product.get('title', ''),
            'category': product.get('category', ''),
            'relevance_score': product.get('relevance_score', 0.0),
            'keywords': ','.join(keywords),
            'top_keywords': ','.join(keywords[:5]) if len(keywords) >= 5 else ','.join(keywords)
        }
        
        # Add individual keyword scores
        for i, kw in enumerate(keyword_scores[:10]):
            meta_entry[f'keyword_{i+1}'] = kw['keyword']
            meta_entry[f'score_{i+1}'] = kw['score']
        
        metadata.append(meta_entry)
    
    return metadata

def export_to_csv(data: List[Dict[str, Any]], output_file: str) -> None:
    """
    Export data to a CSV file.
    
    Args:
        data (list): List of dictionaries to export
        output_file (str): Path to the output CSV file
    """
    if not data:
        raise ValueError("No data to export")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Convert to DataFrame and export
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    
    print(f"Exported {len(data)} records to {output_file}")
