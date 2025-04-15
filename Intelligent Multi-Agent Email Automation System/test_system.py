"""
Test script for the Intelligent Multi-Agent Email Automation System.
This file contains tests for all major components of the system.
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
from backend.models import Email, EmailProvider, Classification, ProcessedData, ResponseData
from backend.database import db
from backend.cache import cache

# Import agent modules
from agents.ingestion.email_ingestion import EmailIngestionAgent
from agents.classification.classification_agent import ClassificationAgent
from agents.summarization.summarization_extraction_agent import SummarizationExtractionAgent
from agents.response.response_generation_agent import ResponseGenerationAgent
from agents.integration.integration_orchestration_agent import IntegrationOrchestrationAgent

class TestEmailAutomationSystem(unittest.TestCase):
    """Test cases for the Email Automation System."""
    
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
        
        # Test email data
        cls.test_email = {
            "message_id": "<test123@example.com>",
            "subject": "Test Email Subject",
            "from_address": "sender@example.com",
            "to": "recipient@example.com",
            "cc": None,
            "body": "This is a test email body. It contains information about a meeting scheduled for tomorrow at 2 PM.",
            "attachments": []
        }
        
        # Test provider data
        cls.test_provider = {
            "type": "gmail",
            "server": "imap.gmail.com",
            "username": "test@gmail.com",
            "password": "test_password",
            "folder": "INBOX",
            "limit": 10
        }
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Close database and cache connections
        asyncio.run(db.close())
        cache.close()
    
    def test_config_loading(self):
        """Test configuration loading."""
        # Check if configuration is loaded
        self.assertIsNotNone(config.get("database.mongodb_url"))
        self.assertIsNotNone(config.get("cache.redis_host"))
        self.assertIsNotNone(config.get("api.port"))
        
        # Check default values
        self.assertEqual(config.get("email_ingestion.batch_size"), 10)
        self.assertEqual(config.get("classification.threshold"), 0.7)
    
    def test_database_operations(self):
        """Test database operations."""
        # Test email save and retrieval
        email_id = asyncio.run(db.save_email(self.test_email))
        self.assertIsNotNone(email_id)
        
        retrieved_email = asyncio.run(db.get_email(email_id))
        self.assertIsNotNone(retrieved_email)
        self.assertEqual(retrieved_email["subject"], self.test_email["subject"])
        
        # Test email update
        update_data = {"subject": "Updated Subject"}
        update_result = asyncio.run(db.update_email(email_id, update_data))
        self.assertTrue(update_result)
        
        updated_email = asyncio.run(db.get_email(email_id))
        self.assertEqual(updated_email["subject"], "Updated Subject")
    
    def test_cache_operations(self):
        """Test cache operations."""
        # Test email caching
        email_id = "test_email_id"
        cache_result = cache.cache_email(email_id, self.test_email)
        self.assertTrue(cache_result)
        
        cached_email = cache.get_cached_email(email_id)
        self.assertIsNotNone(cached_email)
        self.assertEqual(cached_email["subject"], self.test_email["subject"])
        
        # Test settings caching
        settings_data = {"test_setting": "test_value"}
        cache_result = cache.cache_settings(settings_data)
        self.assertTrue(cache_result)
        
        cached_settings = cache.get_cached_settings()
        self.assertIsNotNone(cached_settings)
        self.assertEqual(cached_settings["test_setting"], "test_value")
    
    def test_email_ingestion_agent(self):
        """Test Email Ingestion Agent."""
        # Test email parsing
        parsed_email = self.ingestion_agent.parse_email_data(self.test_email)
        self.assertIsNotNone(parsed_email)
        self.assertEqual(parsed_email["subject"], self.test_email["subject"])
        
        # Test provider validation
        validation_result = self.ingestion_agent.validate_provider(self.test_provider)
        self.assertTrue(validation_result)
    
    def test_classification_agent(self):
        """Test Classification Agent."""
        # Test email classification
        classification_result = self.classification_agent.classify_email(self.test_email)
        self.assertIsNotNone(classification_result)
        self.assertIn("predicted_category", classification_result)
        self.assertIn("confidence", classification_result)
        
        # Test priority assignment
        priority = self.classification_agent.assign_priority(classification_result)
        self.assertIn(priority, ["high", "medium", "low"])
    
    def test_summarization_agent(self):
        """Test Summarization & Extraction Agent."""
        # Test email summarization
        summary = self.summarization_agent.generate_summary(self.test_email)
        self.assertIsNotNone(summary)
        self.assertTrue(len(summary) <= config.get("summarization.summary_max_length", 150))
        
        # Test data extraction
        extractions = self.summarization_agent.extract_data(self.test_email)
        self.assertIsNotNone(extractions)
        self.assertIn("dates_times", extractions)
        self.assertIn("contacts", extractions)
        self.assertIn("tasks", extractions)
    
    def test_response_agent(self):
        """Test Response Generation Agent."""
        # Create classified email
        classified_email = self.test_email.copy()
        classified_email["classification"] = {
            "predicted_category": "important",
            "confidence": 0.85
        }
        
        # Create processed email
        processed_email = classified_email.copy()
        processed_email["processed_data"] = {
            "summary": "Meeting scheduled for tomorrow at 2 PM.",
            "extractions": {
                "dates_times": [{"text": "tomorrow at 2 PM", "type": "datetime"}],
                "contacts": [],
                "tasks": []
            }
        }
        
        # Test response generation
        response = self.response_agent.generate_response(processed_email)
        self.assertIsNotNone(response)
        self.assertIn("response_text", response)
        self.assertIn("auto_send", response)
        
        # Test template selection
        template = self.response_agent.select_template(processed_email)
        self.assertIsNotNone(template)
    
    def test_integration_agent(self):
        """Test Integration & Orchestration Agent."""
        # Create email with response
        email_with_response = self.test_email.copy()
        email_with_response["classification"] = {
            "predicted_category": "important",
            "confidence": 0.85
        }
        email_with_response["processed_data"] = {
            "summary": "Meeting scheduled for tomorrow at 2 PM.",
            "extractions": {
                "dates_times": [{"text": "tomorrow at 2 PM", "type": "datetime"}],
                "contacts": [],
                "tasks": []
            }
        }
        email_with_response["response_data"] = {
            "response_text": "Thank you for your important message. I've reviewed it and noted the meeting scheduled for tomorrow at 2 PM. I'll attend as requested.",
            "auto_send": True,
            "confidence": 0.92
        }
        
        # Test calendar integration
        calendar_result = self.integration_agent.create_calendar_event(email_with_response)
        self.assertIsNotNone(calendar_result)
        
        # Test workflow orchestration
        workflow_result = self.integration_agent.orchestrate_workflow([email_with_response])
        self.assertIsNotNone(workflow_result)
        self.assertIn("emails_processed", workflow_result)
        self.assertIn("status", workflow_result)

if __name__ == "__main__":
    unittest.main()
