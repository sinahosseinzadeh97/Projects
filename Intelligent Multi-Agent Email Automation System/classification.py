"""
API routes for the Classification Agent in the Intelligent Multi-Agent Email Automation System.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, List, Optional
import json

router = APIRouter(
    prefix="/api/classification",
    tags=["classification"],
    responses={404: {"description": "Not found"}},
)

# Mock storage for classification categories and settings
classification_config = {
    "categories": ["important", "promotional", "support", "spam", "other"],
    "model_type": "bert",
    "threshold": 0.7
}

@router.get("/")
async def get_classification_status():
    """Get the status of the Classification Agent."""
    return {
        "status": "active",
        "model_type": classification_config["model_type"],
        "categories": classification_config["categories"],
        "description": "Classification Agent is responsible for categorizing emails into predefined classes."
    }

@router.get("/categories")
async def get_categories():
    """Get all configured classification categories."""
    return {
        "categories": classification_config["categories"]
    }

@router.post("/categories")
async def update_categories(categories: List[str] = Body(...)):
    """Update the classification categories."""
    global classification_config
    
    # Validate categories
    if not categories:
        raise HTTPException(status_code=400, detail="Categories list cannot be empty")
    
    # Update categories
    classification_config["categories"] = categories
    
    return {
        "status": "success",
        "message": "Categories updated successfully",
        "categories": classification_config["categories"]
    }

@router.post("/classify")
async def classify_emails(emails: List[Dict] = Body(...)):
    """
    Classify a batch of emails.
    
    Each email in the list should have at least:
    - message_id: Unique identifier for the email
    - subject: Email subject
    - body: Email body content
    """
    # Validate input
    if not emails:
        raise HTTPException(status_code=400, detail="Emails list cannot be empty")
    
    # This is a mock implementation
    # In a real implementation, this would call the Classification Agent
    
    import random
    
    # Process each email
    classified_emails = []
    for email in emails:
        # Validate required fields
        required_fields = ["message_id", "subject", "body"]
        for field in required_fields:
            if field not in email:
                raise HTTPException(status_code=400, detail=f"Missing required field in email: {field}")
        
        # Mock classification
        categories = classification_config["categories"]
        predicted_category = random.choice(categories)
        
        # Generate random probabilities
        probabilities = {category: random.random() for category in categories}
        
        # Normalize probabilities
        total = sum(probabilities.values())
        probabilities = {k: v/total for k, v in probabilities.items()}
        
        # Ensure predicted category has highest probability
        max_prob = max(probabilities.values())
        probabilities[predicted_category] = max_prob * 1.2
        
        # Normalize again
        total = sum(probabilities.values())
        probabilities = {k: v/total for k, v in probabilities.items()}
        
        # Create classification result
        classification = {
            "message_id": email["message_id"],
            "predicted_category": predicted_category,
            "confidence": probabilities[predicted_category],
            "category_probabilities": probabilities
        }
        
        # Add to classified emails
        classified_email = {
            **email,
            "classification": classification
        }
        
        classified_emails.append(classified_email)
    
    return {
        "status": "success",
        "message": f"Classified {len(classified_emails)} emails",
        "emails": classified_emails
    }

@router.put("/config")
async def update_config(config: Dict = Body(...)):
    """Update the classification agent configuration."""
    global classification_config
    
    # Update configuration
    for key, value in config.items():
        if key in classification_config:
            classification_config[key] = value
    
    return {
        "status": "success",
        "message": "Configuration updated successfully",
        "config": classification_config
    }
