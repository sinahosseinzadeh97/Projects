"""
API routes for the Integration & Orchestration Agent in the Intelligent Multi-Agent Email Automation System.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, List, Optional
import json
from datetime import datetime

router = APIRouter(
    prefix="/api/integration",
    tags=["integration"],
    responses={404: {"description": "Not found"}},
)

# Mock storage for integration and orchestration settings
integration_config = {
    "workflow": {
        "auto_send_enabled": True,
        "batch_size": 10
    },
    "integrations": {
        "calendar": {
            "enabled": True,
            "service": "google_calendar"
        },
        "crm": {
            "enabled": True,
            "service": "salesforce"
        },
        "task_manager": {
            "enabled": True,
            "service": "asana"
        }
    }
}

@router.get("/")
async def get_integration_status():
    """Get the status of the Integration & Orchestration Agent."""
    return {
        "status": "active",
        "workflow": integration_config["workflow"],
        "integrations": integration_config["integrations"],
        "description": "Integration & Orchestration Agent is responsible for coordinating actions between different agents and managing integrations with external services."
    }

@router.put("/config")
async def update_config(config: Dict = Body(...)):
    """Update the integration and orchestration configuration."""
    global integration_config
    
    # Update workflow configuration
    if "workflow" in config:
        integration_config["workflow"].update(config["workflow"])
    
    # Update integrations configuration
    if "integrations" in config:
        for integration_type, integration_settings in config["integrations"].items():
            if integration_type in integration_config["integrations"]:
                integration_config["integrations"][integration_type].update(integration_settings)
    
    return {
        "status": "success",
        "message": "Configuration updated successfully",
        "config": integration_config
    }

@router.post("/process")
async def process_workflow():
    """
    Run the complete email automation workflow.
    
    This endpoint orchestrates the entire process:
    1. Retrieve emails using the Email Ingestion Agent
    2. Classify emails using the Classification Agent
    3. Process emails using the Summarization & Extraction Agent
    4. Generate responses using the Response Generation Agent
    5. Integrate with external services
    6. Send responses if configured to do so
    """
    # This is a mock implementation
    # In a real implementation, this would call the Integration & Orchestration Agent
    
    import random
    
    start_time = datetime.now()
    
    # Mock workflow execution
    # Generate random number of emails processed
    emails_processed = random.randint(5, 20)
    emails_with_responses = random.randint(3, emails_processed)
    emails_auto_sent = random.randint(0, emails_with_responses)
    
    # Generate random number of integrations
    calendar_integrations = random.randint(0, emails_processed // 2)
    crm_integrations = random.randint(0, emails_processed // 3)
    task_integrations = random.randint(0, emails_processed // 4)
    
    # Simulate processing time
    import time
    time.sleep(1)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Prepare workflow results
    results = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration,
        "emails_processed": emails_processed,
        "emails_with_responses": emails_with_responses,
        "emails_auto_sent": emails_auto_sent,
        "emails_with_calendar_integration": calendar_integrations,
        "emails_with_crm_integration": crm_integrations,
        "emails_with_task_integration": task_integrations,
        "status": "success"
    }
    
    return results

@router.post("/calendar/create-event")
async def create_calendar_event(event: Dict = Body(...)):
    """
    Create a calendar event based on extracted information.
    
    Required fields:
    - title: Event title
    - datetime: Date and time of the event
    
    Optional fields:
    - description: Event description
    - attendees: List of attendee email addresses
    - location: Event location
    - duration_minutes: Event duration in minutes (default: 60)
    """
    # Validate input
    required_fields = ["title", "datetime"]
    for field in required_fields:
        if field not in event:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Check if calendar integration is enabled
    if not integration_config["integrations"]["calendar"]["enabled"]:
        return {
            "status": "error",
            "message": "Calendar integration is not enabled",
            "event": None
        }
    
    # This is a mock implementation
    # In a real implementation, this would use calendar APIs to create an event
    
    # Set default values for optional fields
    description = event.get("description", "")
    attendees = event.get("attendees", [])
    location = event.get("location", "")
    duration_minutes = event.get("duration_minutes", 60)
    
    # Create event
    created_event = {
        "id": f"event_{datetime.now().timestamp()}",
        "title": event["title"],
        "datetime": event["datetime"],
        "description": description,
        "attendees": attendees,
        "location": location,
        "duration_minutes": duration_minutes,
        "service": integration_config["integrations"]["calendar"]["service"],
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": "Calendar event created successfully",
        "event": created_event
    }

@router.post("/crm/update-contact")
async def update_crm_contact(contact: Dict = Body(...)):
    """
    Update a contact in the CRM based on extracted information.
    
    Required fields:
    - email: Contact email address
    
    Optional fields:
    - name: Contact name
    - phone: Contact phone number
    - company: Contact company
    - notes: Additional notes
    """
    # Validate input
    if "email" not in contact:
        raise HTTPException(status_code=400, detail="Missing required field: email")
    
    # Check if CRM integration is enabled
    if not integration_config["integrations"]["crm"]["enabled"]:
        return {
            "status": "error",
            "message": "CRM integration is not enabled",
            "contact": None
        }
    
    # This is a mock implementation
    # In a real implementation, this would use CRM APIs to update a contact
    
    # Set default values for optional fields
    name = contact.get("name", "")
    phone = contact.get("phone", "")
    company = contact.get("company", "")
    notes = contact.get("notes", "")
    
    # Update contact
    updated_contact = {
        "id": f"contact_{datetime.now().timestamp()}",
        "email": contact["email"],
        "name": name,
        "phone": phone,
        "company": company,
        "notes": notes,
        "service": integration_config["integrations"]["crm"]["service"],
        "updated_at": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": "CRM contact updated successfully",
        "contact": updated_contact
    }

@router.post("/tasks/create-task")
async def create_task(task: Dict = Body(...)):
    """
    Create a task in the task manager based on extracted information.
    
    Required fields:
    - title: Task title
    
    Optional fields:
    - description: Task description
    - due_date: Task due date
    - priority: Task priority (low, medium, high)
    - assignee: Task assignee email
    """
    # Validate input
    if "title" not in task:
        raise HTTPException(status_code=400, detail="Missing required field: title")
    
    # Check if task manager integration is enabled
    if not integration_config["integrations"]["task_manager"]["enabled"]:
        return {
            "status": "error",
            "message": "Task manager integration is not enabled",
            "task": None
        }
    
    # This is a mock implementation
    # In a real implementation, this would use task manager APIs to create a task
    
    # Set default values for optional fields
    description = task.get("description", "")
    due_date = task.get("due_date", "")
    priority = task.get("priority", "medium")
    assignee = task.get("assignee", "")
    
    # Create task
    created_task = {
        "id": f"task_{datetime.now().timestamp()}",
        "title": task["title"],
        "description": description,
        "due_date": due_date,
        "priority": priority,
        "assignee": assignee,
        "status": "pending",
        "service": integration_config["integrations"]["task_manager"]["service"],
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": "Task created successfully",
        "task": created_task
    }
