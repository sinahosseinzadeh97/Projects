"""
Pydantic schemas for output validation.
"""
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field, validator


class SourceInfo(BaseModel):
    """Source information for data points."""
    name: str = Field(..., description="Name of the source (website, API, etc.)")
    url: Optional[str] = Field(None, description="URL of the source if available")
    accessed_at: Optional[str] = Field(None, description="Timestamp when the source was accessed")


class DataPoint(BaseModel):
    """A single data point with value, source, and confidence."""
    value: Any = Field(..., description="The actual value of the data point")
    sources: List[SourceInfo] = Field(default_factory=list, description="Sources of the information")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")

    @validator('confidence')
    def validate_confidence(cls, v):
        """Ensure confidence is between 0 and 1."""
        if v < 0 or v > 1:
            return max(0, min(1, v))
        return v


class PersonSchema(BaseModel):
    """Schema for person entity information."""
    name: str = Field(..., description="Full name of the person")
    date_of_birth: Optional[DataPoint] = Field(None, description="Birth date of the person")
    place_of_birth: Optional[DataPoint] = Field(None, description="Birth place of the person")
    profession: Optional[DataPoint] = Field(None, description="List of professions")
    biography: Optional[DataPoint] = Field(None, description="Short biography")
    achievements: Optional[DataPoint] = Field(None, description="Notable achievements")
    related_works: Optional[DataPoint] = Field(None, description="Related works (movies, books, etc.)")
    related_images: Optional[DataPoint] = Field(None, description="URLs of related images")
    opinions_reviews: Optional[DataPoint] = Field(None, description="Opinions or reviews")
    summary: Optional[DataPoint] = Field(None, description="Summary of the most important information")
    additional_info: Optional[Dict[str, DataPoint]] = Field(None, description="Any additional information")


class CompanySchema(BaseModel):
    """Schema for company entity information."""
    name: str = Field(..., description="Company name")
    founded: Optional[DataPoint] = Field(None, description="Foundation date")
    headquarters: Optional[DataPoint] = Field(None, description="Headquarters location")
    industry: Optional[DataPoint] = Field(None, description="Industry or sector")
    products_services: Optional[DataPoint] = Field(None, description="Products or services")
    key_people: Optional[DataPoint] = Field(None, description="Key people (CEO, founders, etc.)")
    description: Optional[DataPoint] = Field(None, description="Company description")
    related_images: Optional[DataPoint] = Field(None, description="URLs of related images")
    reviews_opinions: Optional[DataPoint] = Field(None, description="Reviews or opinions")
    summary: Optional[DataPoint] = Field(None, description="Summary of the most important information")
    additional_info: Optional[Dict[str, DataPoint]] = Field(None, description="Any additional information")


class EntityOutput(BaseModel):
    """The main output schema for any entity type."""
    entity_type: str = Field(..., description="Type of entity (person, company, etc.)")
    data: Union[PersonSchema, CompanySchema] = Field(..., description="Entity data")
    query_timestamp: str = Field(..., description="Timestamp of the query")
    processing_time_seconds: float = Field(..., description="Processing time in seconds")
