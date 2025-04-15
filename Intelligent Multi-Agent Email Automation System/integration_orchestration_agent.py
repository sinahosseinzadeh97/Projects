"""
Integration & Orchestration Agent for the Intelligent Multi-Agent Email Automation System.

This agent coordinates and orchestrates actions between the different agents and
manages integrations with external services like calendar systems and CRMs.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegrationOrchestrationAgent:
    """
    Agent responsible for coordinating the workflow between different agents and
    managing integrations with external services.
    
    This agent serves as the central orchestrator for the email automation system,
    ensuring smooth data flow between components and external services.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Integration & Orchestration Agent.
        
        Args:
            config: Configuration dictionary containing workflow and integration settings
        """
        self.config = config
        self.workflow_config = config.get("workflow", {})
        self.integrations = config.get("integrations", {})
        self.logger = logger
        
        # Initialize agent references (will be set later)
        self.email_ingestion_agent = None
        self.classification_agent = None
        self.summarization_extraction_agent = None
        self.response_generation_agent = None
        
    def register_agents(self, 
                        email_ingestion_agent: Any, 
                        classification_agent: Any, 
                        summarization_extraction_agent: Any, 
                        response_generation_agent: Any):
        """
        Register all agent instances with the orchestrator.
        
        Args:
            email_ingestion_agent: Email Ingestion Agent instance
            classification_agent: Classification Agent instance
            summarization_extraction_agent: Summarization & Extraction Agent instance
            response_generation_agent: Response Generation Agent instance
        """
        self.email_ingestion_agent = email_ingestion_agent
        self.classification_agent = classification_agent
        self.summarization_extraction_agent = summarization_extraction_agent
        self.response_generation_agent = response_generation_agent
        
        self.logger.info("All agents registered with the orchestrator")
    
    async def process_emails(self) -> List[Dict]:
        """
        Orchestrate the complete email processing workflow.
        
        Returns:
            List of fully processed emails with all agent outputs
        """
        try:
            # Step 1: Retrieve emails using the Email Ingestion Agent
            self.logger.info("Starting email retrieval")
            emails = await self.email_ingestion_agent.run()
            self.logger.info(f"Retrieved {len(emails)} emails")
            
            if not emails:
                self.logger.info("No emails to process")
                return []
            
            # Step 2: Classify emails using the Classification Agent
            self.logger.info("Starting email classification")
            classified_emails = self.classification_agent.batch_classify(emails)
            self.logger.info(f"Classified {len(classified_emails)} emails")
            
            # Step 3: Process emails using the Summarization & Extraction Agent
            self.logger.info("Starting email summarization and extraction")
            processed_emails = self.summarization_extraction_agent.batch_process(classified_emails)
            self.logger.info(f"Processed {len(processed_emails)} emails")
            
            # Step 4: Generate responses using the Response Generation Agent
            self.logger.info("Starting response generation")
            emails_with_responses = self.response_generation_agent.batch_generate(processed_emails)
            self.logger.info(f"Generated responses for {len(emails_with_responses)} emails")
            
            # Step 5: Integrate with external services
            self.logger.info("Starting integration with external services")
            final_emails = await self.integrate_with_external_services(emails_with_responses)
            self.logger.info(f"Completed external service integration for {len(final_emails)} emails")
            
            return final_emails
            
        except Exception as e:
            self.logger.error(f"Error in email processing workflow: {str(e)}")
            return []
    
    async def integrate_with_external_services(self, emails: List[Dict]) -> List[Dict]:
        """
        Integrate processed emails with external services like calendars and CRMs.
        
        Args:
            emails: List of processed email dictionaries
            
        Returns:
            List of emails with integration results
        """
        try:
            # Process each email for potential integrations
            for email in emails:
                # Skip emails without processed data
                if "processed_data" not in email:
                    continue
                
                # Get extractions from processed data
                extractions = email.get("processed_data", {}).get("extractions", {})
                
                # Check for calendar-related information
                dates_times = extractions.get("dates_times", [])
                if dates_times and self.integrations.get("calendar", {}).get("enabled", False):
                    # Add calendar integration results
                    email["integrations"] = email.get("integrations", {})
                    email["integrations"]["calendar"] = await self._integrate_with_calendar(email, dates_times)
                
                # Check for contact-related information
                contacts = extractions.get("contacts", [])
                if contacts and self.integrations.get("crm", {}).get("enabled", False):
                    # Add CRM integration results
                    email["integrations"] = email.get("integrations", {})
                    email["integrations"]["crm"] = await self._integrate_with_crm(email, contacts)
                
                # Check for task-related information
                tasks = extractions.get("tasks", [])
                if tasks and self.integrations.get("task_manager", {}).get("enabled", False):
                    # Add task manager integration results
                    email["integrations"] = email.get("integrations", {})
                    email["integrations"]["task_manager"] = await self._integrate_with_task_manager(email, tasks)
            
            return emails
            
        except Exception as e:
            self.logger.error(f"Error integrating with external services: {str(e)}")
            return emails
    
    async def _integrate_with_calendar(self, email: Dict, dates_times: List[Dict]) -> Dict:
        """
        Integrate with calendar services to create events or appointments.
        
        Args:
            email: Email dictionary
            dates_times: List of extracted date and time information
            
        Returns:
            Dictionary with calendar integration results
        """
        # This is a placeholder for actual calendar integration logic
        # In a real implementation, this would use calendar APIs to create events
        
        self.logger.info(f"Integrating email with calendar service")
        
        # Simulate calendar integration
        calendar_results = {
            "service": self.integrations.get("calendar", {}).get("service", "generic_calendar"),
            "events_created": [],
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        # Process each date/time entry
        for dt in dates_times:
            # Only process datetime entries (not just dates or times)
            if dt.get("type") == "datetime":
                # Create a calendar event
                event = {
                    "title": email.get("subject", "Meeting"),
                    "datetime": dt.get("text", ""),
                    "description": email.get("processed_data", {}).get("summary", ""),
                    "status": "tentative",
                    "created": True
                }
                
                calendar_results["events_created"].append(event)
        
        self.logger.info(f"Created {len(calendar_results['events_created'])} calendar events")
        return calendar_results
    
    async def _integrate_with_crm(self, email: Dict, contacts: List[Dict]) -> Dict:
        """
        Integrate with CRM services to update contact information.
        
        Args:
            email: Email dictionary
            contacts: List of extracted contact information
            
        Returns:
            Dictionary with CRM integration results
        """
        # This is a placeholder for actual CRM integration logic
        # In a real implementation, this would use CRM APIs to update contacts
        
        self.logger.info(f"Integrating email with CRM service")
        
        # Simulate CRM integration
        crm_results = {
            "service": self.integrations.get("crm", {}).get("service", "generic_crm"),
            "contacts_updated": [],
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        # Process each contact entry
        for contact in contacts:
            # Create or update a contact
            contact_update = {
                "type": contact.get("type", "unknown"),
                "value": contact.get("text", ""),
                "source": "email",
                "updated": True
            }
            
            crm_results["contacts_updated"].append(contact_update)
        
        self.logger.info(f"Updated {len(crm_results['contacts_updated'])} contacts in CRM")
        return crm_results
    
    async def _integrate_with_task_manager(self, email: Dict, tasks: List[Dict]) -> Dict:
        """
        Integrate with task management services to create tasks.
        
        Args:
            email: Email dictionary
            tasks: List of extracted task information
            
        Returns:
            Dictionary with task manager integration results
        """
        # This is a placeholder for actual task manager integration logic
        # In a real implementation, this would use task manager APIs to create tasks
        
        self.logger.info(f"Integrating email with task management service")
        
        # Simulate task manager integration
        task_results = {
            "service": self.integrations.get("task_manager", {}).get("service", "generic_tasks"),
            "tasks_created": [],
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        # Process each task entry
        for task in tasks:
            # Create a task
            task_create = {
                "title": task.get("text", ""),
                "priority": task.get("priority", "medium"),
                "status": "pending",
                "source": "email",
                "source_id": email.get("message_id", ""),
                "created": True
            }
            
            task_results["tasks_created"].append(task_create)
        
        self.logger.info(f"Created {len(task_results['tasks_created'])} tasks in task manager")
        return task_results
    
    async def send_responses(self, emails: List[Dict]) -> List[Dict]:
        """
        Send generated responses based on auto-send settings.
        
        Args:
            emails: List of email dictionaries with response data
            
        Returns:
            List of emails with sending results
        """
        try:
            self.logger.info(f"Processing {len(emails)} emails for sending responses")
            
            # Track emails that were sent automatically
            auto_sent_count = 0
            
            # Process each email
            for email in emails:
                # Skip emails without response data
                if "response_data" not in email:
                    continue
                
                response_data = email["response_data"]
                
                # Check if auto-send is enabled for this response
                if response_data.get("auto_send", False):
                    # This is a placeholder for actual email sending logic
                    # In a real implementation, this would use SMTP to send emails
                    
                    # Simulate sending the email
                    email["response_data"]["sent"] = True
                    email["response_data"]["sent_timestamp"] = datetime.now().isoformat()
                    
                    auto_sent_count += 1
                else:
                    # Mark as not sent
                    email["response_data"]["sent"] = False
            
            self.logger.info(f"Auto-sent {auto_sent_count} email responses")
            return emails
            
        except Exception as e:
            self.logger.error(f"Error sending responses: {str(e)}")
            return emails
    
    async def run_workflow(self) -> Dict:
        """
        Run the complete email automation workflow.
        
        Returns:
            Dictionary with workflow results
        """
        try:
            start_time = datetime.now()
            self.logger.info(f"Starting email automation workflow at {start_time.isoformat()}")
            
            # Step 1: Process emails through all agents
            processed_emails = await self.process_emails()
            
            # Step 2: Send responses if configured to do so
            if self.workflow_config.get("auto_send_enabled", False):
                processed_emails = await self.send_responses(processed_emails)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Prepare workflow results
            results = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "emails_processed": len(processed_emails),
                "emails_with_responses": sum(1 for e in processed_emails if "response_data" in e),
                "emails_auto_sent": sum(1 for e in processed_emails if e.get("response_data", {}).get("sent", False)),
                "emails_with_calendar_integration": sum(1 for e in processed_emails if e.get("integrations", {}).get("calendar")),
                "emails_with_crm_integration": sum(1 for e in processed_emails if e.get("integrations", {}).get("crm")),
                "emails_with_task_integration": sum(1 for e in processed_emails if e.get("integrations", {}).get("task_manager")),
                "status": "success"
            }
            
            self.logger.info(f"Completed email automation workflow in {duration:.2f} seconds")
            self.logger.info(f"Processed {results['emails_processed']} emails")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in workflow execution: {str(e)}")
            
            # Return error results
            return {
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": 0,
                "emails_processed": 0,
                "status": "error",
                "error": str(e)
            }

# Example usage
async def main():
    # Example configuration
    config = {
        "workf
(Content truncated due to size limit. Use line ranges to read in chunks)