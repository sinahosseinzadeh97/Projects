"""
Text preprocessing utilities for NLP tasks.

This module provides functions for cleaning and preprocessing text data
before performing NLP operations like keyword extraction.
"""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

def clean_text(text):
    """
    Clean text by removing special characters, numbers, and extra whitespace.
    
    Args:
        text (str): Input text to clean
        
    Returns:
        str: Cleaned text
    """
    if not isinstance(text, str) or not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def remove_stopwords(text, custom_stopwords=None):
    """
    Remove stopwords from text.
    
    Args:
        text (str): Input text
        custom_stopwords (list, optional): Additional stopwords to remove
        
    Returns:
        str: Text with stopwords removed
    """
    if not isinstance(text, str) or not text:
        return ""
    
    # Get default stopwords
    stop_words = set(stopwords.words('english'))
    
    # Add custom stopwords if provided
    if custom_stopwords:
        stop_words.update(custom_stopwords)
    
    # Tokenize text
    word_tokens = word_tokenize(text)
    
    # Remove stopwords
    filtered_text = [word for word in word_tokens if word not in stop_words]
    
    return ' '.join(filtered_text)

def lemmatize_text(text):
    """
    Lemmatize text to reduce words to their base form.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Lemmatized text
    """
    if not isinstance(text, str) or not text:
        return ""
    
    # Initialize lemmatizer
    lemmatizer = WordNetLemmatizer()
    
    # Tokenize text
    word_tokens = word_tokenize(text)
    
    # Lemmatize each word
    lemmatized_text = [lemmatizer.lemmatize(word) for word in word_tokens]
    
    return ' '.join(lemmatized_text)

def preprocess_text(text, custom_stopwords=None, lemmatize=True):
    """
    Preprocess text by cleaning, removing stopwords, and lemmatizing.
    
    Args:
        text (str): Input text
        custom_stopwords (list, optional): Additional stopwords to remove
        lemmatize (bool): Whether to lemmatize text
        
    Returns:
        str: Preprocessed text
    """
    if not isinstance(text, str) or not text:
        return ""
    
    # Clean text
    cleaned_text = clean_text(text)
    
    # Remove stopwords
    text_without_stopwords = remove_stopwords(cleaned_text, custom_stopwords)
    
    # Lemmatize if requested
    if lemmatize:
        processed_text = lemmatize_text(text_without_stopwords)
    else:
        processed_text = text_without_stopwords
    
    return processed_text
