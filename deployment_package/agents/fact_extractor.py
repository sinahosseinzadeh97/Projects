"""
Fact Extractor Agent for extracting basic factual information about entities.
"""
from typing import Dict, Any, Optional, List
import json

from core.base_agent import BaseAgent
from utils.validation import clean_confidence_score
from schemas.output_schema import DataPoint, SourceInfo


class FactExtractorAgent(BaseAgent):
    """
    Agent responsible for extracting factual information about entities.
    """
    
    def __init__(self, **kwargs):
        """Initialize the fact extractor agent."""
        super().__init__(name="fact_extractor", **kwargs)
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract factual information about an entity.
        
        Args:
            query: The entity to get facts about
            context: Optional context information
            
        Returns:
            Dict[str, Any]: Extracted facts
        """
        entity_type = context.get("entity_type", "person") if context else "person"
        
        # Define the system prompt based on entity type
        system_prompt = self._get_system_prompt(entity_type)
        
        # Define the user prompt
        user_prompt = f"""
        Please extract factual information about "{query}".
        
        Focus on extracting the following key information:
        - Basic identifying information
        - Dates and locations 
        - Professional or main activity details
        - Notable achievements or works
        
        For each fact, provide:
        1. The fact value
        2. The source of this information
        3. A confidence score (0-1) indicating how certain you are about this fact
        
        Format your response as a valid JSON object.
        """
        
        # Query the LLM
        response = self.query_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            json_response=True
        )
        
        # Process and validate the response
        processed_response = self._process_response(response, entity_type)
        
        return processed_response
    
    def _get_system_prompt(self, entity_type: str) -> str:
        """
        Get the appropriate system prompt based on entity type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            str: System prompt
        """
        if entity_type == "person":
            return """
            You are a fact extraction specialist focused on gathering accurate biographical information 
            about people. You should extract key facts like birth date, birth place, profession, 
            notable works, and other relevant biographical details.
            
            For each fact, provide:
            - value: The actual fact
            - sources: List of sources where this information was found
            - confidence: A score between 0-1 indicating your confidence in this fact's accuracy
            
            Return a JSON object with the extracted facts.
            """
        elif entity_type == "company":
            return """
            You are a fact extraction specialist focused on gathering accurate information about companies 
            and organizations. You should extract key facts like founding date, headquarters location, 
            industry, key products or services, and other relevant company details.
            
            For each fact, provide:
            - value: The actual fact
            - sources: List of sources where this information was found
            - confidence: A score between 0-1 indicating your confidence in this fact's accuracy
            
            Return a JSON object with the extracted facts.
            """
        else:
            return """
            You are a fact extraction specialist focused on gathering accurate information about various 
            entities. Extract key identifying and contextual information about the entity in question.
            
            For each fact, provide:
            - value: The actual fact
            - sources: List of sources where this information was found
            - confidence: A score between 0-1 indicating your confidence in this fact's accuracy
            
            Return a JSON object with the extracted facts.
            """
    
    def _process_response(self, response: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """
        Process and validate the LLM response.
        
        Args:
            response: Raw LLM response
            entity_type: Type of entity
            
        Returns:
            Dict[str, Any]: Processed response
        """
        # Handle error cases
        if "error" in response:
            return {
                "error": f"Failed to extract facts: {response.get('error')}",
                "facts": {}
            }
        
        # Convert each fact to our standardized DataPoint format
        processed_facts = {}
        
        # Iterate through all keys in the response
        for key, value in response.items():
            if key == "error":
                continue
                
            # Skip processing time and other metadata keys
            if key in ["processing_time"]:
                processed_facts[key] = value
                continue
            
            # Try to extract the components of a fact
            try:
                if isinstance(value, dict):
                    fact_value = value.get("value")
                    sources_data = value.get("sources", [])
                    
                    # Handle both list and single source formats
                    if not isinstance(sources_data, list):
                        sources_data = [sources_data]
                    
                    # Process sources
                    sources = []
                    for source in sources_data:
                        if isinstance(source, str):
                            sources.append(SourceInfo(name=source, url=None, accessed_at=None))
                        elif isinstance(source, dict):
                            sources.append(SourceInfo(
                                name=source.get("name", "Unknown"),
                                url=source.get("url"),
                                accessed_at=source.get("accessed_at")
                            ))
                    
                    # Get and validate confidence score
                    confidence = clean_confidence_score(value.get("confidence", 0.7))
                    
                    # Create a DataPoint
                    data_point = DataPoint(
                        value=fact_value,
                        sources=sources,
                        confidence=confidence
                    )
                    
                    processed_facts[key] = data_point.dict()
            except Exception as e:
                # Skip facts that fail to process
                print(f"Error processing fact '{key}': {e}")
        
        return {
            "entity_type": entity_type,
            "facts": processed_facts
        }
