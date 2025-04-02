"""
Agent Orchestrator module for coordinating the work of multiple agents.
"""
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from agents.fact_extractor import FactExtractorAgent
from agents.media_fetcher import MediaFetcherAgent
from agents.content_aggregator import ContentAggregatorAgent
from agents.summarizer import SummarizerAgent
from utils.validation import is_valid_person_name, is_valid_company_name, validate_entity_output
from utils.caching import cache_manager
from schemas.output_schema import EntityOutput, PersonSchema, CompanySchema
from config import DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL


class AgentOrchestrator:
    """
    Orchestrator for coordinating the work of multiple agents.
    """
    
    def __init__(self, 
                llm_provider: str = DEFAULT_LLM_PROVIDER, 
                llm_model: str = DEFAULT_LLM_MODEL):
        """
        Initialize the agent orchestrator.
        
        Args:
            llm_provider: LLM provider to use
            llm_model: LLM model to use
        """
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        
        # Initialize agents
        self.fact_extractor = FactExtractorAgent(
            llm_provider_name=llm_provider,
            llm_model=llm_model
        )
        
        self.media_fetcher = MediaFetcherAgent(
            llm_provider_name=llm_provider,
            llm_model=llm_model
        )
        
        self.content_aggregator = ContentAggregatorAgent(
            llm_provider_name=llm_provider,
            llm_model=llm_model
        )
        
        self.summarizer = SummarizerAgent(
            llm_provider_name=llm_provider,
            llm_model=llm_model
        )
    
    def determine_entity_type(self, query: str) -> str:
        """
        Determine the type of entity from the query.
        
        Args:
            query: The input query
            
        Returns:
            str: Entity type ('person', 'company', etc.)
        """
        # Simple heuristic approach - could be replaced with a more sophisticated classifier
        if is_valid_person_name(query):
            return "person"
        elif is_valid_company_name(query):
            return "company"
        else:
            # Default to person if uncertain
            return "person"
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a query through all agents.
        
        Args:
            query: The entity to research
            
        Returns:
            Dict[str, Any]: Combined results from all agents
        """
        # Check cache for full query results
        cache_key = f"full_query:{query}"
        cached_result = cache_manager.get(cache_key, "orchestrator")
        if cached_result:
            return cached_result
        
        # Start timing
        start_time = time.time()
        
        # Determine entity type
        entity_type = self.determine_entity_type(query)
        
        # Create context dictionary to pass between agents
        context = {
            "entity_type": entity_type,
            "query": query
        }
        
        # Step 1: Extract facts
        fact_results = self.fact_extractor.run(query, context)
        context["facts"] = fact_results.get("facts", {})
        
        # Step 2: Fetch media
        media_results = self.media_fetcher.run(query, context)
        context["media"] = media_results.get("media", {})
        
        # Step 3: Aggregate content
        content_results = self.content_aggregator.run(query, context)
        context["content"] = content_results.get("content", {})
        
        # Step 4: Generate summary
        summary_results = self.summarizer.run(query, context)
        context["summary"] = summary_results.get("summary", {})
        
        # Calculate total processing time
        processing_time = time.time() - start_time
        
        # Build the final output
        if entity_type == "person":
            # Build a person schema
            person_data = self._build_person_schema(query, context)
            output = {
                "entity_type": "person",
                "data": person_data,
                "query_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": processing_time
            }
        elif entity_type == "company":
            # Build a company schema
            company_data = self._build_company_schema(query, context)
            output = {
                "entity_type": "company",
                "data": company_data,
                "query_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": processing_time
            }
        else:
            # Generic output
            output = {
                "entity_type": entity_type,
                "data": context,
                "query_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": processing_time
            }
        
        # Validate output
        validated_output = validate_entity_output(output)
        
        # Store in cache
        cache_manager.set(cache_key, "orchestrator", output)
        
        return output
    
    def _build_person_schema(self, name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a person schema from the context data.
        
        Args:
            name: The person's name
            context: Context with facts, media, content, and summary
            
        Returns:
            Dict[str, Any]: Person schema
        """
        facts = context.get("facts", {})
        media = context.get("media", {})
        content = context.get("content", {})
        summary = context.get("summary", {})
        
        # Map facts to person schema fields
        person_data = {
            "name": name
        }
        
        # Map known facts to schema fields
        for fact_key, fact_value in facts.items():
            if fact_key == "date_of_birth" or fact_key == "birth_date":
                person_data["date_of_birth"] = fact_value
            elif fact_key == "place_of_birth" or fact_key == "birth_place":
                person_data["place_of_birth"] = fact_value
            elif fact_key == "profession" or fact_key == "occupation":
                person_data["profession"] = fact_value
            elif fact_key == "biography" or fact_key == "bio":
                person_data["biography"] = fact_value
            elif fact_key == "achievements" or fact_key == "accomplishments":
                person_data["achievements"] = fact_value
            elif fact_key in ["works", "movies", "books", "related_works"]:
                person_data["related_works"] = fact_value
            else:
                # Add to additional info
                if "additional_info" not in person_data:
                    person_data["additional_info"] = {}
                person_data["additional_info"][fact_key] = fact_value
        
        # Add media data
        if media and "images" in media:
            person_data["related_images"] = media["images"]
        
        # Add content data (opinions/reviews)
        for content_type, content_data in content.items():
            if content_type in ["reviews", "opinions", "critiques"]:
                person_data["opinions_reviews"] = content_data
                break
        
        # Add summary
        if "detailed_summary" in summary:
            person_data["summary"] = summary["detailed_summary"]
        
        return person_data
    
    def _build_company_schema(self, name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a company schema from the context data.
        
        Args:
            name: The company name
            context: Context with facts, media, content, and summary
            
        Returns:
            Dict[str, Any]: Company schema
        """
        facts = context.get("facts", {})
        media = context.get("media", {})
        content = context.get("content", {})
        summary = context.get("summary", {})
        
        # Map facts to company schema fields
        company_data = {
            "name": name
        }
        
        # Map known facts to schema fields
        for fact_key, fact_value in facts.items():
            if fact_key in ["founded", "foundation_date", "founding_date"]:
                company_data["founded"] = fact_value
            elif fact_key in ["headquarters", "hq", "location"]:
                company_data["headquarters"] = fact_value
            elif fact_key in ["industry", "sector", "field"]:
                company_data["industry"] = fact_value
            elif fact_key in ["products", "services", "products_and_services", "products_services"]:
                company_data["products_services"] = fact_value
            elif fact_key in ["key_people", "executives", "leadership", "founders"]:
                company_data["key_people"] = fact_value
            elif fact_key in ["description", "about", "overview"]:
                company_data["description"] = fact_value
            else:
                # Add to additional info
                if "additional_info" not in company_data:
                    company_data["additional_info"] = {}
                company_data["additional_info"][fact_key] = fact_value
        
        # Add media data
        if media and "images" in media:
            company_data["related_images"] = media["images"]
        
        # Add content data (reviews/opinions)
        for content_type, content_data in content.items():
            if content_type in ["reviews", "opinions", "critiques"]:
                company_data["reviews_opinions"] = content_data
                break
        
        # Add summary
        if "detailed_summary" in summary:
            company_data["summary"] = summary["detailed_summary"]
        
        return company_data
