"""
Validation utilities for input and output data.
"""
import re
from typing import Dict, Any, Union
from schemas.output_schema import EntityOutput, PersonSchema, CompanySchema, DataPoint, SourceInfo


def is_valid_person_name(name: str) -> bool:
    """
    Validates if the input is likely a person's name.
    
    Args:
        name: The name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Basic validation to check if the name contains alphabetic characters and spaces
    if not name or not isinstance(name, str):
        return False
    
    # Simple pattern matching for name format
    pattern = r'^[A-Za-z\s\'\-\.]+$'
    return bool(re.match(pattern, name))


def is_valid_company_name(name: str) -> bool:
    """
    Validates if the input is likely a company name.
    
    Args:
        name: The company name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False
    
    # Companies can have more characters like & and numbers
    pattern = r'^[A-Za-z0-9\s\'\-\.&,!]+$'
    return bool(re.match(pattern, name))


def validate_entity_output(data: Dict[str, Any]) -> Union[EntityOutput, None]:
    """
    Validates the output data against the defined schema.
    
    Args:
        data: The data to validate
        
    Returns:
        EntityOutput: Validated output or None if validation fails
    """
    try:
        if data.get('entity_type') == 'person':
            person_data = data.get('data', {})
            person_schema = PersonSchema(**person_data)
            return EntityOutput(
                entity_type='person',
                data=person_schema,
                query_timestamp=data.get('query_timestamp'),
                processing_time_seconds=data.get('processing_time_seconds')
            )
        elif data.get('entity_type') == 'company':
            company_data = data.get('data', {})
            company_schema = CompanySchema(**company_data)
            return EntityOutput(
                entity_type='company',
                data=company_schema,
                query_timestamp=data.get('query_timestamp'),
                processing_time_seconds=data.get('processing_time_seconds')
            )
        else:
            return None
    except Exception as e:
        print(f"Validation error: {e}")
        return None


def clean_confidence_score(score: float) -> float:
    """
    Ensures a confidence score is within the valid range (0-1).
    
    Args:
        score: The confidence score
        
    Returns:
        float: The cleaned confidence score
    """
    if isinstance(score, (int, float)):
        return max(0.0, min(1.0, float(score)))
    return 0.0
