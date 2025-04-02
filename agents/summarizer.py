"""
Summarizer Agent for condensing information about entities into concise summaries.
"""
from typing import Dict, Any, Optional, List
import json

from core.base_agent import BaseAgent
from utils.validation import clean_confidence_score
from schemas.output_schema import DataPoint, SourceInfo


class SummarizerAgent(BaseAgent):
    """
    Agent responsible for summarizing information about entities.
    """
    
    def __init__(self, **kwargs):
        """Initialize the summarizer agent."""
        super().__init__(name="summarizer", **kwargs)
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Summarize information about an entity.
        
        Args:
            query: The entity to summarize
            context: Optional context with facts, media, and content
            
        Returns:
            Dict[str, Any]: Summary information
        """
        if not context:
            context = {}
            
        entity_type = context.get("entity_type", "person")
        facts = context.get("facts", {})
        media = context.get("media", {})
        content = context.get("content", {})
        
        # Define the system prompt
        system_prompt = """
        You are a professional summarizer who creates concise, accurate summaries 
        of information about entities. Your summaries should be comprehensive but 
        focused on the most important and relevant details.
        
        Create multiple summary types:
        - brief_summary: A 1-2 sentence overview
        - detailed_summary: A comprehensive paragraph
        - key_points: A bullet list of the most important facts
        - significance: Why this entity is notable or significant
        
        Return your summaries as a JSON object.
        """
        
        # Build the context for the prompt
        context_prompt = "Based on the following information:\n\n"
        
        # Add facts
        if facts:
            context_prompt += "FACTS:\n"
            for key, value in facts.items():
                if isinstance(value, dict) and "value" in value:
                    context_prompt += f"- {key}: {value['value']}\n"
            context_prompt += "\n"
        
        # Add media information (summarized)
        if media:
            context_prompt += "MEDIA:\n"
            for media_type, media_data in media.items():
                if isinstance(media_data, dict) and "value" in media_data:
                    media_items = media_data["value"]
                    if isinstance(media_items, list) and media_items:
                        context_prompt += f"- {media_type.capitalize()}: {len(media_items)} items\n"
                        # Include a couple of examples
                        for i, item in enumerate(media_items[:2]):
                            if "description" in item:
                                context_prompt += f"  * {item['description']}\n"
            context_prompt += "\n"
        
        # Add content information (summarized)
        if content:
            context_prompt += "CONTENT:\n"
            for content_type, content_data in content.items():
                if isinstance(content_data, dict) and "value" in content_data:
                    content_items = content_data["value"]
                    if isinstance(content_items, list) and content_items:
                        context_prompt += f"- {content_type.capitalize()}: {len(content_items)} items\n"
                        # Include a couple of examples
                        for i, item in enumerate(content_items[:2]):
                            if "summary" in item:
                                context_prompt += f"  * {item['summary']}\n"
            context_prompt += "\n"
        
        # Define the user prompt
        user_prompt = f"""
        {context_prompt}
        
        Please create a comprehensive summary about "{query}" who is a {entity_type}.
        
        Provide the following summaries:
        1. A brief overview (1-2 sentences)
        2. A detailed summary paragraph
        3. 5-7 key points about {query}
        4. An explanation of {query}'s significance or importance
        
        Format your response as a valid JSON object with these summary types.
        """
        
        # Query the LLM
        response = self.query_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            json_response=True
        )
        
        # Process and validate the response
        processed_response = self._process_response(response, context)
        
        return processed_response
    
    def _process_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate the LLM response.
        
        Args:
            response: Raw LLM response
            context: The context used for summarization
            
        Returns:
            Dict[str, Any]: Processed response
        """
        # Handle error cases
        if "error" in response:
            return {
                "error": f"Failed to create summary: {response.get('error')}",
                "summary": {}
            }
        
        # Extract sources from the context
        sources = []
        
        # Add fact sources
        facts = context.get("facts", {})
        for fact_key, fact_data in facts.items():
            if isinstance(fact_data, dict) and "sources" in fact_data:
                fact_sources = fact_data.get("sources", [])
                if isinstance(fact_sources, list):
                    for source in fact_sources:
                        if isinstance(source, dict) and "name" in source:
                            source_name = source.get("name")
                            if source_name and source_name not in [s.name for s in sources if hasattr(s, 'name')]:
                                sources.append(SourceInfo(
                                    name=source_name,
                                    url=source.get("url"),
                                    accessed_at=source.get("accessed_at")
                                ))
        
        # Process the summary results
        processed_summary = {}
        
        # Process each summary type
        for key, value in response.items():
            if key in ["processing_time", "error"]:
                continue
            
            # Create a DataPoint for the summary
            try:
                processed_summary[key] = DataPoint(
                    value=value,
                    sources=sources,
                    confidence=0.85  # Summaries generally have high confidence as they're based on vetted data
                ).dict()
            except Exception as e:
                print(f"Error processing summary '{key}': {e}")
        
        return {
            "summary": processed_summary
        }
