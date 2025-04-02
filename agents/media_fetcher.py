"""
Media Fetcher Agent for finding images and other media related to entities.
"""
from typing import Dict, Any, Optional, List
import json

from core.base_agent import BaseAgent
from utils.validation import clean_confidence_score
from schemas.output_schema import DataPoint, SourceInfo


class MediaFetcherAgent(BaseAgent):
    """
    Agent responsible for finding media content related to entities.
    """
    
    def __init__(self, **kwargs):
        """Initialize the media fetcher agent."""
        super().__init__(name="media_fetcher", **kwargs)
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Find media related to an entity.
        
        Args:
            query: The entity to find media for
            context: Optional context information
            
        Returns:
            Dict[str, Any]: Media information
        """
        entity_type = context.get("entity_type", "person") if context else "person"
        entity_facts = context.get("facts", {}) if context else {}
        
        # Define the system prompt
        system_prompt = """
        You are a media research specialist who finds relevant images and media for entities.
        Since you don't have direct access to search for images, you'll generate a list of
        what would be the most relevant media sources and links that could be found for this entity.
        
        For each media item you suggest, provide:
        - description: A description of what the media item would contain
        - likely_source: Where this media would typically be found
        - relevance: How relevant this media would be (0-1 score)
        
        Return your suggestions as a JSON object.
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
        
        Please suggest relevant media related to "{query}".
        
        For a {entity_type}, I'm particularly interested in:
        
        1. Profile/representative images
        2. Images related to their notable works or achievements
        3. Historical images showing key moments
        4. Media coverage references
        
        For each media suggestion, include:
        - A description of what the media would contain
        - Where this media would likely be found (source)
        - How relevant this media would be to understanding {query} (relevance score 0-1)
        
        Format your response as a valid JSON object with media grouped by type.
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
                "error": f"Failed to fetch media: {response.get('error')}",
                "media": {}
            }
        
        # Process the media results
        processed_media = {}
        
        # Categorize media by type
        media_by_type = {
            "images": [],
            "videos": [],
            "articles": [],
            "other": []
        }
        
        # Helper function to determine media type
        def determine_media_type(item):
            desc = item.get("description", "").lower()
            if any(img_term in desc for img_term in ["image", "photo", "picture", "portrait"]):
                return "images"
            elif any(vid_term in desc for vid_term in ["video", "film", "footage"]):
                return "videos"
            elif any(art_term in desc for art_term in ["article", "interview", "news"]):
                return "articles"
            else:
                return "other"
        
        # Process and categorize each media item
        for key, value in response.items():
            if key in ["processing_time", "error"]:
                continue
                
            # If this is a media category, process items inside
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        media_type = determine_media_type(item)
                        media_by_type[media_type].append(item)
            elif isinstance(value, dict):
                # Direct media item
                media_type = determine_media_type(value)
                media_by_type[media_type].append(value)
        
        # Convert each media category to a DataPoint with sources
        for media_type, items in media_by_type.items():
            if not items:
                continue
                
            sources = []
            for item in items:
                source_name = item.get("likely_source", "Unknown")
                description = item.get("description", "")
                
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
            
            # Create the data point for this media type
            processed_media[media_type] = DataPoint(
                value=items,  # Keep the original item details
                sources=sources,
                confidence=confidence
            ).dict()
        
        return {
            "media": processed_media
        }
