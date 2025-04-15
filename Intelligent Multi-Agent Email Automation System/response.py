"""
API routes for the Response Generation Agent in the Intelligent Multi-Agent Email Automation System.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, List, Optional
import json
from datetime import datetime

router = APIRouter(
    prefix="/api/response",
    tags=["response"],
    responses={404: {"description": "Not found"}},
)

# Mock storage for response generation settings
response_config = {
    "model_type": "gpt",
    "auto_send_threshold": 0.9,
    "templates": {
        "important": "Thank you for your important message. I've reviewed it and {summary}. I'll {action} as requested.",
        "support": "Thank you for reaching out to our support team. I understand that {summary}. We'll {action} to resolve this issue.",
        "promotional": "Thank you for sharing this offer. I'll review the details about {summary} and get back to you if interested.",
        "spam": "",  # No response for spam
        "other": "Thank you for your message. I've noted that {summary}. I'll get back to you soon."
    }
}

@router.get("/")
async def get_response_status():
    """Get the status of the Response Generation Agent."""
    return {
        "status": "active",
        "model_type": response_config["model_type"],
        "auto_send_threshold": response_config["auto_send_threshold"],
        "templates_configured": len(response_config["templates"]),
        "description": "Response Generation Agent is responsible for creating intelligent and context-aware reply drafts for emails."
    }

@router.get("/templates")
async def get_templates():
    """Get all configured response templates."""
    return {
        "templates": response_config["templates"]
    }

@router.put("/templates")
async def update_templates(templates: Dict[str, str] = Body(...)):
    """Update the response templates."""
    global response_config
    
    # Update templates
    response_config["templates"].update(templates)
    
    return {
        "status": "success",
        "message": "Templates updated successfully",
        "templates": response_config["templates"]
    }

@router.put("/config")
async def update_config(config: Dict = Body(...)):
    """Update the response generation agent configuration."""
    global response_config
    
    # Update configuration
    for key, value in config.items():
        if key in response_config and key != "templates":
            response_config[key] = value
    
    return {
        "status": "success",
        "message": "Configuration updated successfully",
        "config": {k: v for k, v in response_config.items() if k != "templates"}
    }

@router.post("/generate")
async def generate_responses(emails: List[Dict] = Body(...)):
    """
    Generate responses for a batch of emails.
    
    Each email in the list should have at least:
    - message_id: Unique identifier for the email
    - subject: Email subject
    - from: Sender email address
    - body: Email body content
    
    And optionally:
    - classification: Classification data from the Classification Agent
    - processed_data: Processed data from the Summarization & Extraction Agent
    """
    # Validate input
    if not emails:
        raise HTTPException(status_code=400, detail="Emails list cannot be empty")
    
    # This is a mock implementation
    # In a real implementation, this would call the Response Generation Agent
    
    import random
    
    # Process each email
    emails_with_responses = []
    for email in emails:
        # Validate required fields
        required_fields = ["message_id", "subject", "from", "body"]
        for field in required_fields:
            if field not in email:
                raise HTTPException(status_code=400, detail=f"Missing required field in email: {field}")
        
        # Extract sender information
        from_field = email.get("from", "")
        sender_name = ""
        sender_email = ""
        
        if "<" in from_field and ">" in from_field:
            # Format: "Name <email@example.com>"
            parts = from_field.split("<", 1)
            sender_name = parts[0].strip()
            sender_email = parts[1].split(">", 1)[0].strip()
        else:
            # Just email address
            sender_email = from_field.strip()
            sender_name = sender_email.split("@", 1)[0] if "@" in sender_email else sender_email
        
        # Determine category
        category = "other"
        if "classification" in email:
            category = email["classification"].get("predicted_category", "other")
        
        # Get summary if available
        summary = ""
        if "processed_data" in email:
            summary = email["processed_data"].get("summary", "")
        
        if not summary:
            # Generate a simple summary if not available
            subject = email.get("subject", "")
            body = email.get("body", "")
            summary = subject if len(subject) > 10 else (body[:100] + "..." if len(body) > 100 else body)
        
        # Get template for the category
        template = response_config["templates"].get(category, response_config["templates"]["other"])
        
        # Skip response generation for spam
        if category == "spam":
            response_data = {
                "message_id": email["message_id"],
                "response_text": "",
                "auto_send": False,
                "confidence": 0.0,
                "category": category,
                "generation_timestamp": datetime.now().isoformat()
            }
        else:
            # Prepare template variables
            template_vars = {
                "summary": summary or "your message",
                "action": "take appropriate action"
            }
            
            # Generate response text
            response_text = template.format(**template_vars)
            
            # Add greeting
            greeting = f"Hello {sender_name}," if sender_name else "Hello,"
            response_text = f"{greeting}\n\n{response_text}"
            
            # Add signature
            response_text += "\n\nBest regards,\n[Your Name]"
            
            # Determine confidence and auto-send recommendation
            confidence = 0.85 if category in ["important", "support"] else 0.7
            auto_send = confidence >= response_config["auto_send_threshold"]
            
            response_data = {
                "message_id": email["message_id"],
                "response_text": response_text,
                "auto_send": auto_send,
                "confidence": confidence,
                "category": category,
                "generation_timestamp": datetime.now().isoformat()
            }
        
        # Add to emails with responses
        email_with_response = {
            **email,
            "response_data": response_data
        }
        
        emails_with_responses.append(email_with_response)
    
    return {
        "status": "success",
        "message": f"Generated responses for {len(emails_with_responses)} emails",
        "emails": emails_with_responses
    }

@router.post("/send")
async def send_responses(data: Dict = Body(...)):
    """
    Send generated responses.
    
    Required fields:
    - emails: List of emails with response_data
    
    Optional fields:
    - auto_send_only: Whether to only send responses marked for auto-send (default: true)
    """
    # Validate input
    if "emails" not in data:
        raise HTTPException(status_code=400, detail="Missing required field: emails")
    
    emails = data["emails"]
    auto_send_only = data.get("auto_send_only", True)
    
    # This is a mock implementation
    # In a real implementation, this would use SMTP to send emails
    
    # Track emails that were sent
    sent_count = 0
    emails_with_sending_results = []
    
    for email in emails:
        # Skip emails without response data
        if "response_data" not in email:
            emails_with_sending_results.append(email)
            continue
        
        response_data = email["response_data"]
        
        # Skip empty responses (e.g., for spam)
        if not response_data.get("response_text"):
            emails_with_sending_results.append(email)
            continue
        
        # Check if auto-send is enabled for this response
        if auto_send_only and not response_data.get("auto_send", False):
            emails_with_sending_results.append(email)
            continue
        
        # Simulate sending the email
        email["response_data"]["sent"] = True
        email["response_data"]["sent_timestamp"] = datetime.now().isoformat()
        
        sent_count += 1
        emails_with_sending_results.append(email)
    
    return {
        "status": "success",
        "message": f"Sent {sent_count} email responses",
        "emails": emails_with_sending_results
    }
