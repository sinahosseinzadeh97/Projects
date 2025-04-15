"""
API routes for the Email Ingestion Agent in the Intelligent Multi-Agent Email Automation System.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, List, Optional
import json

router = APIRouter(
    prefix="/api/ingestion",
    tags=["ingestion"],
    responses={404: {"description": "Not found"}},
)

# Mock storage for email provider configurations
email_providers = []

@router.get("/")
async def get_ingestion_status():
    """Get the status of the Email Ingestion Agent."""
    return {
        "status": "active",
        "providers_configured": len(email_providers),
        "description": "Email Ingestion Agent is responsible for connecting to email providers and retrieving emails."
    }

@router.get("/providers")
async def get_providers():
    """Get all configured email providers."""
    return {
        "providers": email_providers
    }

@router.post("/providers")
async def add_provider(provider: Dict = Body(...)):
    """
    Add a new email provider configuration.
    
    Required fields:
    - type: Provider type (e.g., gmail, outlook)
    - server: IMAP server address
    - username: Email account username
    - password: Email account password (or app password)
    
    Optional fields:
    - folder: Email folder to fetch from (default: INBOX)
    - limit: Maximum number of emails to fetch (default: 10)
    """
    # Validate required fields
    required_fields = ["type", "server", "username", "password"]
    for field in required_fields:
        if field not in provider:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Add default values for optional fields
    if "folder" not in provider:
        provider["folder"] = "INBOX"
    if "limit" not in provider:
        provider["limit"] = 10
    
    # Add provider ID
    provider["id"] = len(email_providers) + 1
    
    # Add to providers list
    email_providers.append(provider)
    
    return {
        "status": "success",
        "message": f"Added {provider['type']} provider with ID {provider['id']}",
        "provider_id": provider["id"]
    }

@router.delete("/providers/{provider_id}")
async def remove_provider(provider_id: int):
    """Remove an email provider configuration by ID."""
    global email_providers
    
    # Find provider by ID
    for i, provider in enumerate(email_providers):
        if provider.get("id") == provider_id:
            # Remove provider
            removed = email_providers.pop(i)
            return {
                "status": "success",
                "message": f"Removed {removed['type']} provider with ID {provider_id}"
            }
    
    raise HTTPException(status_code=404, detail=f"Provider with ID {provider_id} not found")

@router.post("/fetch")
async def fetch_emails(params: Dict = Body(default={})):
    """
    Fetch emails from configured providers.
    
    Optional parameters:
    - provider_id: ID of specific provider to fetch from (default: all providers)
    - limit: Maximum number of emails to fetch per provider (default: use provider config)
    """
    provider_id = params.get("provider_id")
    limit = params.get("limit")
    
    # This is a mock implementation
    # In a real implementation, this would call the Email Ingestion Agent
    
    # Prepare response
    response = {
        "status": "success",
        "message": "Emails fetched successfully",
        "providers_processed": 0,
        "emails_fetched": 0,
        "emails": []
    }
    
    # Check if we have any providers configured
    if not email_providers:
        return {
            "status": "warning",
            "message": "No email providers configured",
            "providers_processed": 0,
            "emails_fetched": 0,
            "emails": []
        }
    
    # Process providers
    for provider in email_providers:
        # Skip if specific provider_id was requested and doesn't match
        if provider_id is not None and provider["id"] != provider_id:
            continue
        
        # Use provider limit if no specific limit was provided
        provider_limit = limit if limit is not None else provider["limit"]
        
        # Mock fetching emails
        mock_emails = [
            {
                "message_id": f"<mock{i}@{provider['type']}.com>",
                "subject": f"Mock Email {i} from {provider['type']}",
                "from": f"sender{i}@example.com",
                "to": provider["username"],
                "body": f"This is a mock email body for testing purposes.\n\nRegards,\nSender {i}",
                "date": "2025-04-14T07:00:00Z",
                "provider_id": provider["id"],
                "provider_type": provider["type"]
            }
            for i in range(1, provider_limit + 1)
        ]
        
        # Add to response
        response["emails"].extend(mock_emails)
        response["providers_processed"] += 1
        response["emails_fetched"] += len(mock_emails)
    
    return response
