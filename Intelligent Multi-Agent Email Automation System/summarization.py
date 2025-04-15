"""
API routes for the Summarization & Extraction Agent in the Intelligent Multi-Agent Email Automation System.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, List, Optional
import json
from datetime import datetime

router = APIRouter(
    prefix="/api/summarization",
    tags=["summarization"],
    responses={404: {"description": "Not found"}},
)

# Mock storage for summarization settings
summarization_config = {
    "model_type": "gpt",
    "summary_max_length": 150
}

@router.get("/")
async def get_summarization_status():
    """Get the status of the Summarization & Extraction Agent."""
    return {
        "status": "active",
        "model_type": summarization_config["model_type"],
        "summary_max_length": summarization_config["summary_max_length"],
        "description": "Summarization & Extraction Agent is responsible for generating concise summaries and extracting key data points from emails."
    }

@router.put("/config")
async def update_config(config: Dict = Body(...)):
    """Update the summarization agent configuration."""
    global summarization_config
    
    # Update configuration
    for key, value in config.items():
        if key in summarization_config:
            summarization_config[key] = value
    
    return {
        "status": "success",
        "message": "Configuration updated successfully",
        "config": summarization_config
    }

@router.post("/process")
async def process_emails(emails: List[Dict] = Body(...)):
    """
    Process a batch of emails to generate summaries and extract key information.
    
    Each email in the list should have at least:
    - message_id: Unique identifier for the email
    - subject: Email subject
    - body: Email body content
    """
    # Validate input
    if not emails:
        raise HTTPException(status_code=400, detail="Emails list cannot be empty")
    
    # This is a mock implementation
    # In a real implementation, this would call the Summarization & Extraction Agent
    
    import re
    import random
    
    # Process each email
    processed_emails = []
    for email in emails:
        # Validate required fields
        required_fields = ["message_id", "subject", "body"]
        for field in required_fields:
            if field not in email:
                raise HTTPException(status_code=400, detail=f"Missing required field in email: {field}")
        
        # Generate mock summary
        subject = email.get("subject", "")
        body = email.get("body", "")
        
        # Simple extractive summarization as a placeholder
        sentences = re.split(r'(?<=[.!?])\s+', body)
        sentences = [s for s in sentences if len(s) > 10]
        
        if sentences:
            summary_sentences = sentences[:min(3, len(sentences))]
            summary = " ".join(summary_sentences)
            
            # Truncate if too long
            if len(summary) > summarization_config["summary_max_length"]:
                summary = summary[:summarization_config["summary_max_length"]] + "..."
        else:
            summary = "No content available for summarization."
        
        # Mock extractions
        # Dates and times
        dates_times = []
        if "Tuesday" in body or "Monday" in body or "Wednesday" in body or "Thursday" in body or "Friday" in body:
            dates_times.append({
                "text": "next Tuesday at 2:30 PM",
                "type": "datetime"
            })
        
        # Contacts
        contacts = []
        if "@" in body:
            contacts.append({
                "text": "john.doe@example.com",
                "type": "email"
            })
        
        if "phone" in body.lower() or "call" in body.lower():
            contacts.append({
                "text": "(555) 123-4567",
                "type": "phone"
            })
        
        # Tasks
        tasks = []
        if "please" in body.lower() or "could you" in body.lower() or "can you" in body.lower():
            tasks.append({
                "text": "review the attached document",
                "type": "task",
                "priority": "medium",
                "status": "pending"
            })
        
        # Create processed data
        processed_data = {
            "message_id": email["message_id"],
            "summary": summary,
            "extractions": {
                "dates_times": dates_times,
                "contacts": contacts,
                "tasks": tasks
            },
            "processing_timestamp": datetime.now().isoformat()
        }
        
        # Add to processed emails
        processed_email = {
            **email,
            "processed_data": processed_data
        }
        
        processed_emails.append(processed_email)
    
    return {
        "status": "success",
        "message": f"Processed {len(processed_emails)} emails",
        "emails": processed_emails
    }

@router.post("/summarize")
async def summarize_text(data: Dict = Body(...)):
    """
    Generate a summary for a given text.
    
    Required fields:
    - text: The text to summarize
    
    Optional fields:
    - max_length: Maximum length of the summary (default: from config)
    """
    # Validate input
    if "text" not in data:
        raise HTTPException(status_code=400, detail="Missing required field: text")
    
    text = data["text"]
    max_length = data.get("max_length", summarization_config["summary_max_length"])
    
    # This is a mock implementation
    # In a real implementation, this would use a more sophisticated summarization algorithm
    
    import re
    
    # Simple extractive summarization
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s for s in sentences if len(s) > 10]
    
    if sentences:
        summary_sentences = sentences[:min(3, len(sentences))]
        summary = " ".join(summary_sentences)
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
    else:
        summary = "No content available for summarization."
    
    return {
        "status": "success",
        "original_length": len(text),
        "summary_length": len(summary),
        "summary": summary
    }

@router.post("/extract")
async def extract_information(data: Dict = Body(...)):
    """
    Extract key information from a given text.
    
    Required fields:
    - text: The text to extract information from
    
    Optional fields:
    - extract_dates: Whether to extract dates and times (default: true)
    - extract_contacts: Whether to extract contact information (default: true)
    - extract_tasks: Whether to extract tasks (default: true)
    """
    # Validate input
    if "text" not in data:
        raise HTTPException(status_code=400, detail="Missing required field: text")
    
    text = data["text"]
    extract_dates = data.get("extract_dates", True)
    extract_contacts = data.get("extract_contacts", True)
    extract_tasks = data.get("extract_tasks", True)
    
    # This is a mock implementation
    # In a real implementation, this would use more sophisticated extraction algorithms
    
    import re
    
    extractions = {}
    
    # Extract dates and times
    if extract_dates:
        dates_times = []
        date_patterns = [
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b',
            r'\b(tomorrow|today|yesterday)\b',
            r'\b(next|this|last)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dates_times.append({
                    "text": match.group(0),
                    "type": "date"
                })
        
        extractions["dates_times"] = dates_times
    
    # Extract contacts
    if extract_contacts:
        contacts = []
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b'
        
        for match in re.finditer(email_pattern, text):
            contacts.append({
                "text": match.group(0),
                "type": "email"
            })
        
        for match in re.finditer(phone_pattern, text):
            contacts.append({
                "text": match.group(0),
                "type": "phone"
            })
        
        extractions["contacts"] = contacts
    
    # Extract tasks
    if extract_tasks:
        tasks = []
        task_patterns = [
            r'(?:please|kindly|could you|can you)\s+([^.!?]+[.!?])',
            r'(?:need to|must|should|have to)\s+([^.!?]+[.!?])',
            r'(?:todo|to-do|to do|action item|task):\s*([^.!?]+[.!?])'
        ]
        
        for pattern in task_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                task_text = match.group(1).strip() if match.groups() else match.group(0).strip()
                tasks.append({
                    "text": task_text,
                    "type": "task",
                    "priority": "medium",
                    "status": "pending"
                })
        
        extractions["tasks"] = tasks
    
    return {
        "status": "success",
        "extractions": extractions
    }
