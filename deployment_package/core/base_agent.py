"""
Base agent class that all specialized agents will inherit from.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time

from core.llm_provider import llm_provider
from utils.caching import cache_manager
from config import DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL


class BaseAgent(ABC):
    """
    Base agent class with common functionality.
    """
    
    def __init__(self, 
                 name: str, 
                 llm_provider_name: str = DEFAULT_LLM_PROVIDER,
                 llm_model: str = DEFAULT_LLM_MODEL):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name
            llm_provider_name: Name of the LLM provider to use
            llm_model: Model to use
        """
        self.name = name
        self.llm_provider_name = llm_provider_name
        self.llm_model = llm_model
        self.cache_enabled = True
    
    def get_from_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache if available.
        
        Args:
            query: The query to look up
            
        Returns:
            Optional[Dict[str, Any]]: Cached data or None
        """
        if not self.cache_enabled:
            return None
        
        return cache_manager.get(query, self.name)
    
    def save_to_cache(self, query: str, data: Dict[str, Any]) -> None:
        """
        Save data to cache.
        
        Args:
            query: The query to cache
            data: Data to cache
        """
        if not self.cache_enabled:
            return
        
        cache_manager.set(query, self.name, data)
    
    def query_llm(self, 
                 prompt: str, 
                 system_prompt: Optional[str] = None,
                 json_response: bool = True) -> Dict[str, Any]:
        """
        Query the LLM with the given prompt.
        
        Args:
            prompt: The prompt to send
            system_prompt: Optional system prompt
            json_response: Whether to request JSON response
            
        Returns:
            Dict[str, Any]: LLM response
        """
        return llm_provider.query_llm(
            provider=self.llm_provider_name,
            prompt=prompt,
            system_prompt=system_prompt,
            json_response=json_response,
            model=self.llm_model
        )
    
    @abstractmethod
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query with this agent.
        
        Args:
            query: The query to process
            context: Optional context information
            
        Returns:
            Dict[str, Any]: Processing result
        """
        pass
    
    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the agent with timing and caching.
        
        Args:
            query: The query to process
            context: Optional context information
            
        Returns:
            Dict[str, Any]: Processing result
        """
        # Check cache
        cached_result = self.get_from_cache(query)
        if cached_result:
            return cached_result
        
        # Process the query
        start_time = time.time()
        result = self.process(query, context)
        processing_time = time.time() - start_time
        
        # Add processing time to result
        if isinstance(result, dict):
            result["processing_time"] = processing_time
        
        # Save to cache
        self.save_to_cache(query, result)
        
        return result
