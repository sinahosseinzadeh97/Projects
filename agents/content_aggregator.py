"""
Content Aggregator Agent for collecting and organizing content about entities.
"""
from typing import Dict, Any, Optional, List
import json

from core.base_agent import BaseAgent
from utils.validation import clean_confidence_score
from schemas.output_schema import DataPoint, SourceInfo


class ContentAggregatorAgent(BaseAgent):
    """
    Agent responsible for collecting and aggregating content about entities.
    """
    
    def __init__(self, **kwargs):
        """Initialize the content aggregator agent."""
        super().__init__(name="content_aggregator", **kwargs)
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Aggregate content related to an entity.
        
        Args:
            query: The entity to get content for
            context: Optional context information
            
        Returns:
            Dict[str, Any]: Aggregated content
        """
        entity_type = context.get("entity_type", "person") if context else "person"
        entity_facts = context.get("facts", {}) if context else {}
        
        # Define the system prompt based on entity type
        system_prompt = """
        You are a content research specialist who aggregates information about entities 
        from various sources. Your task is to find and organize opinions, reviews, 
        articles, and other relevant content.
        
        For each content item you identify, include:
        - content_type: Type of content (review, opinion, article, etc.)
        - summary: A brief summary of what the content contains
        - source: Where this content would likely be found
        - sentiment: The sentiment of the content (positive, negative, neutral)
        - relevance: How relevant and important this content is (0-1 score)
        
        Return your findings as a JSON object.
        """
        
        # Define the user prompt, incorporating known facts for context
        facts_context = ""
        if entity_facts:
            facts_context = "Based on these known facts:\n"
            for key, value in entity_facts.items():
                if isinstance(value, dict) and "value" in value:
                    facts_context += f"- {key}: {value['value']}\n"
        
        user_prompt = f"""
        {facts_context}
        
        Please aggregate content related to "{query}".
        
        For a {entity_type}, collect and organize content like:
        
        1. Reviews or critical analysis of their work
        2. Public opinions or sentiment
        3. Articles or features about them
        4. Recent news or developments
        5. Controversies or notable events
        
        For each content item, include:
        - The type of content
        - A summary of what it contains
        - Likely source of the content
        - The sentiment (positive, negative, neutral)
        - Relevance score (0-1)
        
        Format your response as a valid JSON object with content grouped by type.
        """
        
        # Query the LLM
        response = self.query_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            json_response=True
        )
        
        # Process and validate the response
        processed_response = self._process_response(response)
        
        return processed_response
    
    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate the LLM response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Dict[str, Any]: Processed response
        """
        # Handle error cases
        if "error" in response:
            return {
                "error": f"Failed to aggregate content: {response.get('error')}",
                "content": {}
            }
        
        # Process the content results
        processed_content = {}
        
        # Group content by type
        content_by_type = {}
        
        # Process each content category or item
        for key, value in response.items():
            if key in ["processing_time", "error"]:
                continue
                
            # If this is a content category with list of items
            if isinstance(value, list):
                content_type = key
                if content_type not in content_by_type:
                    content_by_type[content_type] = []
                
                for item in value:
                    if isinstance(item, dict):
                        # Add the category as content_type if not already present
                        if "content_type" not in item:
                            item["content_type"] = content_type
                        content_by_type[content_type].append(item)
            
            # If this is a direct content item
            elif isinstance(value, dict):
                content_type = value.get("content_type", key)
                if content_type not in content_by_type:
                    content_by_type[content_type] = []
                content_by_type[content_type].append(value)
        
        # Convert each content category to a DataPoint with sources
        for content_type, items in content_by_type.items():
            if not items:
                continue
                
            sources = []
            for item in items:
                source_name = item.get("source", "Unknown")
                
                sources.append(SourceInfo(
                    name=source_name,
                    url=None,  # We don't have actual URLs
                    accessed_at=None
                ))
            
            # Calculate average relevance or use default
            relevance_scores = [
                clean_confidence_score(item.get("relevance", 0.7))
                for item in items if "relevance" in item
            ]
            
            confidence = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.7
            
            # Create the data point for this content type
            processed_content[content_type] = DataPoint(
                value=items,  # Keep the original item details
                sources=sources,
                confidence=confidence
            ).dict()
        
        return {
            "content": processed_content
        }
