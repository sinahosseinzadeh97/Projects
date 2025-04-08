"""
Data filtering module for applying filters to product data.

This module provides functions for filtering products based on
categories, relevance scores, and keyword presence.
"""

from typing import List, Dict, Any, Optional, Tuple

def filter_by_category(products: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, Any]]:
    """
    Filter products by category.
    
    Args:
        products (list): List of product dictionaries
        categories (list): List of categories to include
        
    Returns:
        list: Filtered list of product dictionaries
    """
    if not categories:
        return products
    
    return [p for p in products if p.get('category') in categories]

def filter_by_relevance_score(products: List[Dict[str, Any]], min_score: float = 0.0) -> List[Dict[str, Any]]:
    """
    Filter products by minimum relevance score.
    
    Args:
        products (list): List of product dictionaries
        min_score (float, optional): Minimum relevance score
        
    Returns:
        list: Filtered list of product dictionaries
    """
    return [p for p in products if p.get('relevance_score', 0.0) >= min_score]

def filter_by_keyword_presence(products: List[Dict[str, Any]], keywords: List[str], match_all: bool = False) -> List[Dict[str, Any]]:
    """
    Filter products by keyword presence.
    
    Args:
        products (list): List of product dictionaries
        keywords (list): List of keywords to match
        match_all (bool, optional): Whether to match all keywords (AND) or any keyword (OR)
        
    Returns:
        list: Filtered list of product dictionaries
    """
    if not keywords:
        return products
    
    filtered_products = []
    
    for product in products:
        product_keywords = product.get('keywords', [])
        
        if match_all:
            # Match all keywords (AND)
            if all(kw in product_keywords for kw in keywords):
                filtered_products.append(product)
        else:
            # Match any keyword (OR)
            if any(kw in product_keywords for kw in keywords):
                filtered_products.append(product)
    
    return filtered_products

def filter_by_price_range(products: List[Dict[str, Any]], min_price: float = 0.0, max_price: float = float('inf')) -> List[Dict[str, Any]]:
    """
    Filter products by price range.
    
    Args:
        products (list): List of product dictionaries
        min_price (float, optional): Minimum price
        max_price (float, optional): Maximum price
        
    Returns:
        list: Filtered list of product dictionaries
    """
    return [p for p in products if min_price <= p.get('price', 0.0) <= max_price]

def filter_by_text_search(products: List[Dict[str, Any]], search_term: str, fields: List[str] = None) -> List[Dict[str, Any]]:
    """
    Filter products by text search across specified fields.
    
    Args:
        products (list): List of product dictionaries
        search_term (str): Search term
        fields (list, optional): Fields to search in (defaults to title, description, features)
        
    Returns:
        list: Filtered list of product dictionaries
    """
    if not search_term:
        return products
    
    if fields is None:
        fields = ['title', 'description', 'features']
    
    search_term = search_term.lower()
    filtered_products = []
    
    for product in products:
        for field in fields:
            field_value = product.get(field, '')
            if isinstance(field_value, str) and search_term in field_value.lower():
                filtered_products.append(product)
                break
    
    return filtered_products

def apply_filters(products: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply multiple filters to products.
    
    Args:
        products (list): List of product dictionaries
        filters (dict): Dictionary of filters to apply
        
    Returns:
        list: Filtered list of product dictionaries
    """
    filtered_products = products
    
    # Apply category filter
    if 'categories' in filters and filters['categories']:
        filtered_products = filter_by_category(filtered_products, filters['categories'])
    
    # Apply relevance score filter
    if 'min_relevance_score' in filters:
        filtered_products = filter_by_relevance_score(filtered_products, filters['min_relevance_score'])
    
    # Apply keyword presence filter
    if 'keywords' in filters and filters['keywords']:
        match_all = filters.get('match_all_keywords', False)
        filtered_products = filter_by_keyword_presence(filtered_products, filters['keywords'], match_all)
    
    # Apply price range filter
    min_price = filters.get('min_price', 0.0)
    max_price = filters.get('max_price', float('inf'))
    filtered_products = filter_by_price_range(filtered_products, min_price, max_price)
    
    # Apply text search filter
    if 'search_term' in filters and filters['search_term']:
        search_fields = filters.get('search_fields', None)
        filtered_products = filter_by_text_search(filtered_products, filters['search_term'], search_fields)
    
    return filtered_products
