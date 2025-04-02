"""
Simple caching system to reduce API calls and improve performance.
"""
import json
import os
import time
from typing import Dict, Any, Optional
import hashlib

from config import CACHE_ENABLED, CACHE_EXPIRY


class CacheManager:
    """
    Manages caching of API responses to reduce redundant calls.
    """
    
    def __init__(self):
        """Initialize the cache manager."""
        self.cache_dir = ".cache"
        self.ensure_cache_dir()
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
    
    def ensure_cache_dir(self):
        """Create the cache directory if it doesn't exist."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def generate_key(self, query: str, query_type: str) -> str:
        """
        Generate a unique cache key for a query.
        
        Args:
            query: The query string
            query_type: Type of query (e.g., 'fact', 'media')
            
        Returns:
            str: A unique cache key
        """
        hash_input = f"{query.lower().strip()}:{query_type}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def get(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache if it exists and is not expired.
        
        Args:
            query: The query string
            query_type: Type of query
            
        Returns:
            Optional[Dict[str, Any]]: Cached data or None if not found or expired
        """
        if not CACHE_ENABLED:
            return None
        
        key = self.generate_key(query, query_type)
        
        # Check memory cache first
        if key in self.memory_cache:
            cache_entry = self.memory_cache[key]
            if time.time() - cache_entry.get('timestamp', 0) < CACHE_EXPIRY:
                return cache_entry.get('data')
        
        # Check file cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    if time.time() - cache_data.get('timestamp', 0) < CACHE_EXPIRY:
                        # Update memory cache
                        self.memory_cache[key] = cache_data
                        return cache_data.get('data')
            except Exception as e:
                print(f"Cache read error: {e}")
        
        return None
    
    def set(self, query: str, query_type: str, data: Dict[str, Any]) -> None:
        """
        Save data to cache.
        
        Args:
            query: The query string
            query_type: Type of query
            data: Data to cache
        """
        if not CACHE_ENABLED:
            return
        
        key = self.generate_key(query, query_type)
        cache_entry = {
            'timestamp': time.time(),
            'data': data
        }
        
        # Update memory cache
        self.memory_cache[key] = cache_entry
        
        # Update file cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_entry, f)
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def clear(self, query: Optional[str] = None, query_type: Optional[str] = None) -> None:
        """
        Clear cache entries.
        
        Args:
            query: Specific query to clear (or all if None)
            query_type: Specific query type to clear (or all if None)
        """
        if query and query_type:
            key = self.generate_key(query, query_type)
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
        else:
            # Clear all cache
            self.memory_cache = {}
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))


# Singleton instance
cache_manager = CacheManager()
