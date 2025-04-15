"""
Integration test script for the Intelligent Multi-Agent Email Automation System.
This file contains end-to-end tests for the complete workflow.
"""

import unittest
import asyncio
import json
import os
import sys
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import backend modules
from backend.config import config
from backend.database import db
from backend.cache import cache

# Import agent modules
from agents.ingestion.email_ingestion import EmailIngestionAgent
from agents.classification.classification_agent import ClassificationAgent
from agents.summarization.summarization_extraction_agent import SummarizationExtractionAgent
from agents.response.response_generation_agent import ResponseGenerationAgent
from agents.integration.integration_orchestration_agent import IntegrationOrchestrationAgent

class TestEndToEndWorkflow(unittest.TestCase):
    """Test cases for the end-to-end workflow."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Initialize database and cache
        asyncio.run(db.connect())
        cache.connect()
        
        # Create test agents
        cls.ingestion_agent = EmailIngestionAgent()
        cls.classification_agent = ClassificationAgent()
        cls.summarization_agent = SummarizationExtractionAgent()
        cls.response_agent = ResponseGenerationAgent()
        cls.integration_agent = IntegrationOrchestrationAgent()
        
        # Test emails
        cls.test_emails = [
            {
                "message_id": "<test123@example.com>",
                "subject": "Project Update Meeting",
                "from_address": "john.doe@example.com",
                "to": "recipient@example.com",
                "cc": "team@example.com",
                "body": "Hello team,\n\nLet's schedule a project update meeting for tomorrow at 2 PM. We need to discuss the current progress and next steps.\n\nRegards,\nJohn",
                "attachments": []
            },
            {
                "message_id": "<test456@example.com>",
                "subject": "Weekly Newsletter",
                "from_address": "newsletter@company.com",
                "to": "recipient@example.com",
                "cc": None,
                "body": "This week's newsletter includes updates on new products, upcoming events, and company announcements. Check out our latest blog post!",
                "attachments": []
            },
            {
                "message_id": "<test789@example.com>",
                "subject": "Support Request #12345",
                "from_address": "customer@client.org",
                "to": "support@example.com",
                "cc": "recipient@example.com",
                "body": "I'm experiencing issues with logging into my account. The password reset functionality doesn't seem to be working. Can you please help me resolve this issue?",
                "attachments": []
            }
        ]
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Close database and cache connections
        asyncio.run(db.close())
        cache.close()
    
    async def process_email(self, email):
        """Process a single email through the entire workflow."""
        # Step 1: Save email to database
        email_id = await db.save_email(email)
        self.assertIsNotNone(email_id)
        
        # Step 2: Classify email
        classification_result = self.classification_agent.classify_email(email)
        self.assertIsNotNone(classification_result)
        
        # Update email with classification
        classified_email = email.copy()
        classified_email["classification"] = classification_result
        await db.update_email(email_id, {"classification": classification_result})
        
        # Step 3: Summarize and extract data
        summary = self.summarization_agent.generate_summary(classified_email)
        self.assertIsNotNone(summary)
        
        extractions = self.summarization_agent.extract_data(classified_email)
        self.assertIsNotNone(extractions)
        
        processed_data = {
            "summary": summary,
            "extractions": extractions,
            "processing_timestamp": datetime.now().isoformat()
        }
        
        # Update email with processed data
        processed_email = classified_email.copy()
        processed_email["processed_data"] = processed_data
        await db.update_email(email_id, {"processed_data": processed_data})
        
        # Step 4: Generate response
        response_data = self.response_agent.generate_response(processed_email)
        self.assertIsNotNone(response_data)
        
        # Update email with response data
        email_with_response = processed_email.copy()
        email_with_response["response_data"] = response_data
        await db.update_email(email_id, {"response_data": response_data})
        
        # Step 5: Handle integrations
        if "dates_times" in extractions and extractions["dates_times"]:
            calendar_result = self.integration_agent.create_calendar_event(email_with_response)
            self.assertIsNotNone(calendar_result)
        
        if "contacts" in extractions and extractions["contacts"]:
            crm_result = self.integration_agent.update_crm_contacts(email_with_response)
            self.assertIsNotNone(crm_result)
        
        if "tasks" in extractions and extractions["tasks"]:
            task_result = self.integration_agent.create_tasks(email_with_response)
            self.assertIsNotNone(task_result)
        
        # Return the fully processed email
        return email_with_response
    
    def test_end_to_end_workflow(self):
        """Test the complete end-to-end workflow."""
        # Process all test emails
        processed_emails = []
        for email in self.test_emails:
            processed_email = asyncio.run(self.process_email(email))
            processed_emails.append(processed_email)
        
        # Verify all emails were processed
        self.assertEqual(len(processed_emails), len(self.test_emails))
        
        # Run workflow orchestration
        workflow_result = self.integration_agent.orchestrate_workflow(processed_emails)
        self.assertIsNotNone(workflow_result)
        self.assertEqual(workflow_result["emails_processed"], len(self.test_emails))
        self.assertEqual(workflow_result["status"], "completed")
        
        # Verify each email has the expected components
        for email in processed_emails:
            self.assertIn("classification", email)
            self.assertIn("processed_data", email)
            self.assertIn("response_data", email)
            
            # Verify classification
            self.assertIn("predicted_category", email["classification"])
            self.assertIn("confidence", email["classification"])
            
            # Verify processed data
            self.assertIn("summary", email["processed_data"])
            self.assertIn("extractions", email["processed_data"])
            
            # Verify response data
            self.assertIn("response_text", email["response_data"])
            self.assertIn("auto_send", email["response_data"])
            self.assertIn("confidence", email["response_data"])

if __name__ == "__main__":
    unittest.main()
