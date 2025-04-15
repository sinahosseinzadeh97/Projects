"""
Database configuration for the Intelligent Multi-Agent Email Automation System.
This file sets up the MongoDB connection and provides database access functions.
"""

import motor.motor_asyncio
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from typing import Dict, List, Optional, Any
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "email_automation")

# Collections
EMAILS_COLLECTION = "emails"
PROVIDERS_COLLECTION = "email_providers"
TEMPLATES_COLLECTION = "response_templates"
SETTINGS_COLLECTION = "settings"
INTEGRATIONS_COLLECTION = "integrations"
ANALYTICS_COLLECTION = "analytics"

class Database:
    """Database class for MongoDB operations."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.client = None
        self.db = None
        self.logger = logger
        
    async def connect(self):
        """Connect to MongoDB."""
        try:
            # Create async client
            self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
            
            # Get database
            self.db = self.client[DATABASE_NAME]
            
            # Verify connection
            await self.client.admin.command('ping')
            
            self.logger.info(f"Connected to MongoDB at {MONGODB_URL}")
            return True
            
        except ConnectionFailure as e:
            self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    async def close(self):
        """Close the database connection."""
        if self.client:
            self.client.close()
            self.logger.info("Closed MongoDB connection")
    
    async def save_email(self, email: Dict) -> str:
        """
        Save an email to the database.
        
        Args:
            email: Email data dictionary
            
        Returns:
            ID of the inserted document
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in email:
                email["timestamp"] = datetime.now().isoformat()
            
            # Insert email
            result = await self.db[EMAILS_COLLECTION].insert_one(email)
            
            self.logger.info(f"Saved email with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            self.logger.error(f"Error saving email: {str(e)}")
            return None
    
    async def get_email(self, email_id: str) -> Optional[Dict]:
        """
        Get an email by ID.
        
        Args:
            email_id: Email document ID
            
        Returns:
            Email data dictionary or None if not found
        """
        try:
            from bson.objectid import ObjectId
            
            # Get email
            email = await self.db[EMAILS_COLLECTION].find_one({"_id": ObjectId(email_id)})
            
            return email
            
        except Exception as e:
            self.logger.error(f"Error getting email: {str(e)}")
            return None
    
    async def update_email(self, email_id: str, update_data: Dict) -> bool:
        """
        Update an email document.
        
        Args:
            email_id: Email document ID
            update_data: Data to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            from bson.objectid import ObjectId
            
            # Update email
            result = await self.db[EMAILS_COLLECTION].update_one(
                {"_id": ObjectId(email_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Updated email with ID: {email_id}")
                return True
            else:
                self.logger.warning(f"No changes made to email with ID: {email_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error updating email: {str(e)}")
            return False
    
    async def get_emails(self, query: Dict = None, limit: int = 100, skip: int = 0) -> List[Dict]:
        """
        Get emails matching a query.
        
        Args:
            query: Query dictionary
            limit: Maximum number of emails to return
            skip: Number of emails to skip
            
        Returns:
            List of email dictionaries
        """
        try:
            # Default query
            if query is None:
                query = {}
            
            # Get emails
            cursor = self.db[EMAILS_COLLECTION].find(query).sort("timestamp", -1).skip(skip).limit(limit)
            
            emails = await cursor.to_list(length=limit)
            
            self.logger.info(f"Retrieved {len(emails)} emails")
            return emails
            
        except Exception as e:
            self.logger.error(f"Error getting emails: {str(e)}")
            return []
    
    async def save_provider(self, provider: Dict) -> str:
        """
        Save an email provider configuration.
        
        Args:
            provider: Provider configuration dictionary
            
        Returns:
            ID of the inserted document
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in provider:
                provider["timestamp"] = datetime.now().isoformat()
            
            # Insert provider
            result = await self.db[PROVIDERS_COLLECTION].insert_one(provider)
            
            self.logger.info(f"Saved provider with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            self.logger.error(f"Error saving provider: {str(e)}")
            return None
    
    async def get_providers(self) -> List[Dict]:
        """
        Get all email provider configurations.
        
        Returns:
            List of provider dictionaries
        """
        try:
            # Get providers
            cursor = self.db[PROVIDERS_COLLECTION].find()
            
            providers = await cursor.to_list(length=100)
            
            self.logger.info(f"Retrieved {len(providers)} providers")
            return providers
            
        except Exception as e:
            self.logger.error(f"Error getting providers: {str(e)}")
            return []
    
    async def save_template(self, template: Dict) -> str:
        """
        Save a response template.
        
        Args:
            template: Template dictionary
            
        Returns:
            ID of the inserted document
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in template:
                template["timestamp"] = datetime.now().isoformat()
            
            # Insert template
            result = await self.db[TEMPLATES_COLLECTION].insert_one(template)
            
            self.logger.info(f"Saved template with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            self.logger.error(f"Error saving template: {str(e)}")
            return None
    
    async def get_templates(self, category: str = None) -> List[Dict]:
        """
        Get response templates.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of template dictionaries
        """
        try:
            # Prepare query
            query = {}
            if category:
                query["category"] = category
            
            # Get templates
            cursor = self.db[TEMPLATES_COLLECTION].find(query)
            
            templates = await cursor.to_list(length=100)
            
            self.logger.info(f"Retrieved {len(templates)} templates")
            return templates
            
        except Exception as e:
            self.logger.error(f"Error getting templates: {str(e)}")
            return []
    
    async def save_settings(self, settings: Dict) -> bool:
        """
        Save system settings.
        
        Args:
            settings: Settings dictionary
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Add timestamp
            settings["updated_at"] = datetime.now().isoformat()
            
            # Update settings (upsert)
            result = await self.db[SETTINGS_COLLECTION].update_one(
                {"_id": "system_settings"},
                {"$set": settings},
                upsert=True
            )
            
            self.logger.info("Saved system settings")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")
            return False
    
    async def get_settings(self) -> Dict:
        """
        Get system settings.
        
        Returns:
            Settings dictionary
        """
        try:
            # Get settings
            settings = await self.db[SETTINGS_COLLECTION].find_one({"_id": "system_settings"})
            
            if not settings:
                # Return default settings if none found
                return {
                    "_id": "system_settings",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            
            return settings
            
        except Exception as e:
            self.logger.error(f"Error getting settings: {str(e)}")
            return {}
    
    async def log_analytics(self, analytics_data: Dict) -> str:
        """
        Log analytics data.
        
        Args:
            analytics_data: Analytics data dictionary
            
        Returns:
            ID of the inserted document
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in analytics_data:
                analytics_data["timestamp"] = datetime.now().isoformat()
            
            # Insert analytics data
            result = await self.db[ANALYTICS_COLLECTION].insert_one(analytics_data)
            
            self.logger.info(f"Logged analytics with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            self.logger.error(f"Error logging analytics: {str(e)}")
            return None
    
    async def get_analytics(self, start_date: str = None, end_date: str = None, limit: int = 100) -> List[Dict]:
        """
        Get analytics data.
        
        Args:
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            limit: Maximum number of records to return
            
        Returns:
            List of analytics dictionaries
        """
        try:
            # Prepare query
            query = {}
            if start_date or end_date:
                query["timestamp"] = {}
                if start_date:
                    query["timestamp"]["$gte"] = start_date
                if end_date:
                    query["timestamp"]["$lte"] = end_date
            
            # Get analytics
            cursor = self.db[ANALYTICS_COLLECTION].find(query).sort("timestamp", -1).limit(limit)
            
            analytics = await cursor.to_list(length=limit)
            
            self.logger.info(f"Retrieved {len(analytics)} analytics records")
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting analytics: {str(e)}")
            return []

# Create database instance
db = Database()

# Example usage
async def main():
    # Connect to database
    await db.connect()
    
    # Example email
    email = {
        "message_id": "<example123@mail.com>",
        "subject": "Test Email",
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "body": "This is a test email.",
        "timestamp": datetime.now().isoformat()
    }
    
    # Save email
    email_id = await db.save_email(email)
    print(f"Saved email with ID: {email_id}")
    
    # Close connection
    await db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
