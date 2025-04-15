"""
Test script for the API endpoints of the Intelligent Multi-Agent Email Automation System.
This file contains tests for all API routes.
"""

import unittest
import requests
import json
import os
from datetime import datetime

class TestAPIEndpoints(unittest.TestCase):
    """Test cases for the API endpoints."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # API base URL
        cls.base_url = "http://localhost:8000"
        
        # Test user credentials
        cls.credentials = {
            "username": "admin",
            "password": "adminpassword"
        }
        
        # Get authentication token
        cls.token = cls.get_auth_token()
        
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
    def get_auth_token(cls):
        """Get authentication token."""
        try:
            response = requests.post(
                f"{cls.base_url}/token",
                data=cls.credentials
            )
            if response.status_code == 200:
                return response.json().get("access_token")
            return None
        except:
            return None
    
    def get_headers(self):
        """Get request headers with authentication token."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        try:
            response = requests.get(f"{self.base_url}/")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("message", data)
            self.assertIn("version", data)
        except requests.RequestException:
            self.skipTest("API server not running")
    
    def test_health_check(self):
        """Test health check endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("status", data)
            self.assertIn("database", data)
            self.assertIn("cache", data)
        except requests.RequestException:
            self.skipTest("API server not running")
    
    def test_authentication(self):
        """Test authentication endpoints."""
        try:
            # Test token endpoint
            response = requests.post(
                f"{self.base_url}/token",
                data=self.credentials
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("access_token", data)
            self.assertIn("token_type", data)
            
            # Test user info endpoint
            headers = self.get_headers()
            if headers["Authorization"] != "Bearer None":
                response = requests.get(
                    f"{self.base_url}/users/me/",
                    headers=headers
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["username"], self.credentials["username"])
        except requests.RequestException:
            self.skipTest("API server not running")
    
    def test_email_ingestion_endpoints(self):
        """Test email ingestion endpoints."""
        try:
            headers = self.get_headers()
            if headers["Authorization"] == "Bearer None":
                self.skipTest("Authentication token not available")
            
            # Test provider creation
            response = requests.post(
                f"{self.base_url}/ingestion/providers",
                headers=headers,
                json=self.test_provider
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("id", data)
            provider_id = data["id"]
            
            # Test provider retrieval
            response = requests.get(
                f"{self.base_url}/ingestion/providers/{provider_id}",
                headers=headers
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["username"], self.test_provider["username"])
            
            # Test email fetching
            response = requests.post(
                f"{self.base_url}/ingestion/fetch",
                headers=headers,
                json={"provider_id": provider_id}
            )
            self.assertEqual(response.status_code, 200)
        except requests.RequestException:
            self.skipTest("API server not running")
    
    def test_classification_endpoints(self):
        """Test classification endpoints."""
        try:
            headers = self.get_headers()
            if headers["Authorization"] == "Bearer None":
                self.skipTest("Authentication token not available")
            
            # Test email classification
            response = requests.post(
                f"{self.base_url}/classification/classify",
                headers=headers,
                json=self.test_email
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("predicted_category", data)
            self.assertIn("confidence", data)
        except requests.RequestException:
            self.skipTest("API server not running")
    
    def test_summarization_endpoints(self):
        """Test summarization endpoints."""
        try:
            headers = self.get_headers()
            if headers["Authorization"] == "Bearer None":
                self.skipTest("Authentication token not available")
            
            # Test email summarization
            response = requests.post(
                f"{self.base_url}/summarization/summarize",
                headers=headers,
                json=self.test_email
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("summary", data)
            
            # Test data extraction
            response = requests.post(
                f"{self.base_url}/summarization/extract",
                headers=headers,
                json=self.test_email
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("extractions", data)
        except requests.RequestException:
            self.skipTest("API server not running")
    
    def test_response_endpoints(self):
        """Test response endpoints."""
        try:
            headers = self.get_headers()
            if headers["Authorization"] == "Bearer None":
                self.skipTest("Authentication token not available")
            
            # Create classified and processed email
            classified_email = self.test_email.copy()
            classified_email["classification"] = {
                "predicted_category": "important",
                "confidence": 0.85
            }
            classified_email["processed_data"] = {
                "summary": "Meeting scheduled for tomorrow at 2 PM.",
                "extractions": {
                    "dates_times": [{"text": "tomorrow at 2 PM", "type": "datetime"}],
                    "contacts": [],
                    "tasks": []
                }
            }
            
            # Test response generation
            response = requests.post(
                f"{self.base_url}/response/generate",
                headers=headers,
                json=classified_email
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("response_text", data)
            self.assertIn("auto_send", data)
        except requests.RequestException:
            self.skipTest("API server not running")
    
    def test_integration_endpoints(self):
        """Test integration endpoints."""
        try:
            headers = self.get_headers()
            if headers["Authorization"] == "Bearer None":
                self.skipTest("Authentication token not available")
            
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
            response = requests.post(
                f"{self.base_url}/integration/calendar",
                headers=headers,
                json=email_with_response
            )
            self.assertEqual(response.status_code, 200)
            
            # Test workflow orchestration
            response = requests.post(
                f"{self.base_url}/integration/workflow",
                headers=headers,
                json=[email_with_response]
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("emails_processed", data)
            self.assertIn("status", data)
        except requests.RequestException:
            self.skipTest("API server not running")

if __name__ == "__main__":
    unittest.main()
