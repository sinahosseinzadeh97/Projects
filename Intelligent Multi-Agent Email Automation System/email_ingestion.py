"""
Email Ingestion Agent for the Intelligent Multi-Agent Email Automation System.

This agent is responsible for connecting to email providers using IMAP/SMTP protocols 
and APIs, retrieving and parsing emails, then forwarding the content to subsequent agents.
"""

import asyncio
import email
import imaplib
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailIngestionAgent:
    """
    Agent responsible for retrieving emails from various providers.
    
    This agent connects to email servers, retrieves new emails,
    parses them, and prepares them for processing by other agents.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Email Ingestion Agent.
        
        Args:
            config: Configuration dictionary containing email provider details
        """
        self.config = config
        self.email_providers = config.get("email_providers", [])
        self.logger = logger
        
    async def connect_to_provider(self, provider_config: Dict) -> Optional[imaplib.IMAP4_SSL]:
        """
        Connect to an email provider using IMAP.
        
        Args:
            provider_config: Configuration for the specific email provider
            
        Returns:
            IMAP connection object or None if connection fails
        """
        try:
            provider_type = provider_config.get("type", "").lower()
            server = provider_config.get("server")
            username = provider_config.get("username")
            password = provider_config.get("password")
            
            if not all([server, username, password]):
                self.logger.error(f"Missing configuration for provider {provider_type}")
                return None
                
            # Connect to the IMAP server
            mail = imaplib.IMAP4_SSL(server)
            mail.login(username, password)
            self.logger.info(f"Successfully connected to {provider_type} ({server})")
            return mail
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {provider_config.get('type')}: {str(e)}")
            return None
    
    async def fetch_emails(self, mail: imaplib.IMAP4_SSL, folder: str = "INBOX", limit: int = 10) -> List[Dict]:
        """
        Fetch emails from a specific folder.
        
        Args:
            mail: IMAP connection object
            folder: Email folder to fetch from
            limit: Maximum number of emails to fetch
            
        Returns:
            List of parsed email dictionaries
        """
        try:
            # Select the mailbox/folder
            status, messages = mail.select(folder)
            if status != "OK":
                self.logger.error(f"Failed to select folder {folder}")
                return []
                
            # Search for all emails in the folder
            status, data = mail.search(None, "ALL")
            if status != "OK":
                self.logger.error("Failed to search for emails")
                return []
                
            # Get email IDs
            email_ids = data[0].split()
            if not email_ids:
                self.logger.info(f"No emails found in folder {folder}")
                return []
                
            # Limit the number of emails to fetch
            email_ids = email_ids[-limit:] if limit > 0 else email_ids
            
            parsed_emails = []
            for email_id in email_ids:
                status, data = mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    self.logger.error(f"Failed to fetch email with ID {email_id}")
                    continue
                    
                raw_email = data[0][1]
                parsed_email = self.parse_email(raw_email)
                if parsed_email:
                    parsed_emails.append(parsed_email)
            
            return parsed_emails
            
        except Exception as e:
            self.logger.error(f"Error fetching emails: {str(e)}")
            return []
    
    def parse_email(self, raw_email: bytes) -> Optional[Dict]:
        """
        Parse a raw email into a structured dictionary.
        
        Args:
            raw_email: Raw email content in bytes
            
        Returns:
            Dictionary containing parsed email data or None if parsing fails
        """
        try:
            msg = email.message_from_bytes(raw_email)
            
            # Extract basic email information
            email_data = {
                "message_id": msg.get("Message-ID", ""),
                "subject": msg.get("Subject", ""),
                "from": msg.get("From", ""),
                "to": msg.get("To", ""),
                "cc": msg.get("Cc", ""),
                "date": msg.get("Date", ""),
                "timestamp": datetime.now().isoformat(),
                "body": "",
                "attachments": []
            }
            
            # Extract email body and attachments
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    # Handle email body
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        email_data["body"] = part.get_payload(decode=True).decode()
                    
                    # Handle attachments
                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            attachment_data = {
                                "filename": filename,
                                "content_type": content_type,
                                "size": len(part.get_payload(decode=True))
                            }
                            email_data["attachments"].append(attachment_data)
            else:
                # Handle plain text emails
                email_data["body"] = msg.get_payload(decode=True).decode()
            
            return email_data
            
        except Exception as e:
            self.logger.error(f"Error parsing email: {str(e)}")
            return None
    
    async def process_provider(self, provider_config: Dict) -> List[Dict]:
        """
        Process emails from a specific provider.
        
        Args:
            provider_config: Configuration for the specific email provider
            
        Returns:
            List of parsed emails from the provider
        """
        mail = await self.connect_to_provider(provider_config)
        if not mail:
            return []
            
        try:
            folder = provider_config.get("folder", "INBOX")
            limit = provider_config.get("limit", 10)
            
            emails = await self.fetch_emails(mail, folder, limit)
            self.logger.info(f"Retrieved {len(emails)} emails from {provider_config.get('type')}")
            
            return emails
            
        except Exception as e:
            self.logger.error(f"Error processing provider {provider_config.get('type')}: {str(e)}")
            return []
            
        finally:
            # Close the connection
            try:
                mail.close()
                mail.logout()
            except:
                pass
    
    async def run(self) -> List[Dict]:
        """
        Run the Email Ingestion Agent to retrieve emails from all configured providers.
        
        Returns:
            List of all retrieved emails from all providers
        """
        all_emails = []
        
        # Process each provider in parallel
        tasks = [self.process_provider(provider) for provider in self.email_providers]
        results = await asyncio.gather(*tasks)
        
        # Combine results from all providers
        for provider_emails in results:
            all_emails.extend(provider_emails)
            
        self.logger.info(f"Total emails retrieved: {len(all_emails)}")
        return all_emails

# Example usage
async def main():
    # Example configuration
    config = {
        "email_providers": [
            {
                "type": "gmail",
                "server": "imap.gmail.com",
                "username": "example@gmail.com",
                "password": "app_password_here",
                "folder": "INBOX",
                "limit": 10
            }
        ]
    }
    
    agent = EmailIngestionAgent(config)
    emails = await agent.run()
    print(f"Retrieved {len(emails)} emails")

if __name__ == "__main__":
    asyncio.run(main())
