"""
LLM provider module for interacting with various LLM APIs.
"""
import json
import os
import time
from typing import Dict, Any, List, Optional
import requests
from openai import OpenAI

from config import OPENAI_API_KEY, MAX_REQUESTS_PER_MINUTE
from utils.caching import cache_manager

class RateLimiter:
    """Simple rate limiter to prevent API rate limit errors."""
    
    def __init__(self, max_requests_per_minute: int):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests_per_minute: Maximum number of requests allowed per minute
        """
        self.max_requests = max_requests_per_minute
        self.window_size = 60  # 1 minute in seconds
        self.request_timestamps: List[float] = []
    
    def wait_if_needed(self) -> None:
        """
        Wait if we've exceeded the rate limit.
        """
        current_time = time.time()
        
        # Remove timestamps older than the window size
        self.request_timestamps = [ts for ts in self.request_timestamps 
                                 if current_time - ts < self.window_size]
        
        # If we've reached the limit, wait until we can make another request
        if len(self.request_timestamps) >= self.max_requests:
            oldest_timestamp = min(self.request_timestamps)
            wait_time = self.window_size - (current_time - oldest_timestamp)
            if wait_time > 0:
                time.sleep(wait_time)
        
        # Add the current request timestamp
        self.request_timestamps.append(time.time())


class LLMProvider:
    """
    Provider for LLM API interactions.
    """
    
    def __init__(self):
        """Initialize the LLM provider."""
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.rate_limiter = RateLimiter(MAX_REQUESTS_PER_MINUTE)
    
    def query_openai(self, 
                    prompt: str, 
                    system_prompt: Optional[str] = None,
                    json_response: bool = True,
                    model: str = "gpt-4o") -> Dict[str, Any]:
        """
        Query OpenAI API.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            json_response: Whether to request JSON response
            model: The model to use
            
        Returns:
            Dict[str, Any]: API response
        """
        # Check cache first
        cache_key = f"{prompt}:{system_prompt or ''}:{model}"
        cached_result = cache_manager.get(cache_key, "openai_query")
        if cached_result:
            return cached_result
        
        # Wait if needed to respect rate limits
        self.rate_limiter.wait_if_needed()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": model,  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                           # do not change this unless explicitly requested by the user
            "messages": messages,
        }
        
        if json_response:
            kwargs["response_format"] = {"type": "json_object"}
        
        try:
            response = self.openai_client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            
            # Parse JSON response if requested
            result = {}
            if json_response:
                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    result = {"error": "Failed to parse JSON response", "raw_content": content}
            else:
                result = {"content": content}
            
            # Cache the result
            cache_manager.set(cache_key, "openai_query", result)
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def query_llm(self, 
                 provider: str, 
                 prompt: str, 
                 system_prompt: Optional[str] = None,
                 json_response: bool = True,
                 model: Optional[str] = None) -> Dict[str, Any]:
        """
        Query a specific LLM provider.
        
        Args:
            provider: The provider to use (e.g., 'openai', 'gemini')
            prompt: The user prompt
            system_prompt: Optional system prompt
            json_response: Whether to request JSON response
            model: The model to use
            
        Returns:
            Dict[str, Any]: API response
        """
        if provider == "openai":
            return self.query_openai(prompt, system_prompt, json_response, model or "gpt-4o")
        
        # Future support for other providers can be added here
        raise ValueError(f"Unsupported LLM provider: {provider}")


# Create a singleton instance
llm_provider = LLMProvider()
