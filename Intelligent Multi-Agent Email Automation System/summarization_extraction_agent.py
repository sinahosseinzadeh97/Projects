"""
Summarization & Extraction Agent for the Intelligent Multi-Agent Email Automation System.

This agent processes emails to generate concise summaries and extract key data points
(meeting times, tasks, contact details) using modern LLMs.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SummarizationExtractionAgent:
    """
    Agent responsible for summarizing emails and extracting key information.
    
    This agent uses NLP models to generate concise summaries of emails and
    extract important data points such as dates, meeting times, tasks, and contacts.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Summarization & Extraction Agent.
        
        Args:
            config: Configuration dictionary containing model settings
        """
        self.config = config
        self.model_type = config.get("model_type", "gpt")
        self.summary_max_length = config.get("summary_max_length", 150)
        self.model = None
        self.logger = logger
        
        # Initialize the model
        self._initialize_model()
        
    def _initialize_model(self):
        """
        Initialize the NLP model for summarization and extraction.
        
        This is a placeholder for actual model initialization.
        In a real implementation, this would load a pre-trained model.
        """
        self.logger.info(f"Initializing {self.model_type} model for summarization and extraction")
        
        # Placeholder for model initialization
        # In a real implementation, this would use a library like transformers to load a model
        # Example:
        # from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        # self.tokenizer = AutoTokenizer.from_pretrained("t5-base")
        # self.model = AutoModelForSeq2SeqLM.from_pretrained("t5-base")
        
        self.logger.info("Model initialized successfully")
    
    def generate_summary(self, email_data: Dict) -> str:
        """
        Generate a concise summary of the email content.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Summarized text
        """
        try:
            subject = email_data.get("subject", "")
            body = email_data.get("body", "")
            
            # Combine subject and body for summarization
            full_text = f"{subject}\n\n{body}"
            
            # This is a placeholder for actual summarization logic
            # In a real implementation, this would use the loaded model to generate a summary
            
            # Simple extractive summarization as a placeholder
            # In a real implementation, this would be replaced with model-generated summary
            sentences = re.split(r'(?<=[.!?])\s+', full_text)
            
            # Filter out empty sentences and very short ones
            sentences = [s for s in sentences if len(s) > 10]
            
            # Select the first few sentences as a simple summary
            # In a real implementation, this would be a more sophisticated algorithm
            if sentences:
                summary_sentences = sentences[:min(3, len(sentences))]
                summary = " ".join(summary_sentences)
                
                # Truncate if too long
                if len(summary) > self.summary_max_length:
                    summary = summary[:self.summary_max_length] + "..."
            else:
                summary = "No content available for summarization."
            
            self.logger.info(f"Generated summary of length {len(summary)}")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return "Failed to generate summary due to an error."
    
    def extract_dates_and_times(self, text: str) -> List[Dict]:
        """
        Extract dates and times from the email text.
        
        Args:
            text: Email text content
            
        Returns:
            List of extracted date and time information
        """
        try:
            # This is a placeholder for actual date/time extraction logic
            # In a real implementation, this would use more sophisticated NLP techniques
            
            # Simple regex patterns for date/time extraction
            date_patterns = [
                r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',  # MM/DD/YYYY or DD/MM/YYYY
                r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b',  # Month DD, YYYY
                r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})\b',  # DD Month YYYY
                r'\b(tomorrow|today|yesterday)\b',  # Relative dates
                r'\b(next|this|last)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b'  # Relative weekdays
            ]
            
            time_patterns = [
                r'\b(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(am|pm|AM|PM)?\b',  # HH:MM(:SS) (AM/PM)
                r'\b(\d{1,2})\s*(am|pm|AM|PM)\b',  # HH AM/PM
                r'\b(noon|midnight)\b'  # Special times
            ]
            
            # Extract dates
            dates = []
            for pattern in date_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    dates.append({
                        "text": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "type": "date"
                    })
            
            # Extract times
            times = []
            for pattern in time_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    times.append({
                        "text": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "type": "time"
                    })
            
            # Combine nearby date and time entries
            datetime_entries = []
            for date in dates:
                # Check if there's a time entry close to this date
                for time in times:
                    # If time is within 20 characters of date, consider them related
                    if abs(time["start"] - date["end"]) < 20 or abs(date["start"] - time["end"]) < 20:
                        datetime_entries.append({
                            "text": f"{date['text']} {time['text']}",
                            "date_text": date["text"],
                            "time_text": time["text"],
                            "type": "datetime"
                        })
            
            # Add remaining dates and times as separate entries
            all_entries = datetime_entries.copy()
            
            # Add dates that weren't combined with times
            for date in dates:
                if not any(entry.get("date_text") == date["text"] for entry in datetime_entries):
                    all_entries.append({
                        "text": date["text"],
                        "type": "date"
                    })
            
            # Add times that weren't combined with dates
            for time in times:
                if not any(entry.get("time_text") == time["text"] for entry in datetime_entries):
                    all_entries.append({
                        "text": time["text"],
                        "type": "time"
                    })
            
            self.logger.info(f"Extracted {len(all_entries)} date/time entries")
            return all_entries
            
        except Exception as e:
            self.logger.error(f"Error extracting dates and times: {str(e)}")
            return []
    
    def extract_contacts(self, text: str) -> List[Dict]:
        """
        Extract contact information from the email text.
        
        Args:
            text: Email text content
            
        Returns:
            List of extracted contact information
        """
        try:
            # This is a placeholder for actual contact extraction logic
            # In a real implementation, this would use more sophisticated NLP techniques
            
            # Simple regex patterns for contact extraction
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\b(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b'
            name_pattern = r'(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            
            # Extract emails
            emails = []
            for match in re.finditer(email_pattern, text):
                emails.append({
                    "text": match.group(0),
                    "type": "email"
                })
            
            # Extract phone numbers
            phones = []
            for match in re.finditer(phone_pattern, text):
                phones.append({
                    "text": match.group(0),
                    "type": "phone"
                })
            
            # Extract names
            names = []
            for match in re.finditer(name_pattern, text):
                names.append({
                    "text": match.group(0),
                    "type": "name"
                })
            
            # Combine all contact information
            contacts = emails + phones + names
            
            self.logger.info(f"Extracted {len(contacts)} contact entries")
            return contacts
            
        except Exception as e:
            self.logger.error(f"Error extracting contacts: {str(e)}")
            return []
    
    def extract_tasks(self, text: str) -> List[Dict]:
        """
        Extract tasks and action items from the email text.
        
        Args:
            text: Email text content
            
        Returns:
            List of extracted tasks
        """
        try:
            # This is a placeholder for actual task extraction logic
            # In a real implementation, this would use more sophisticated NLP techniques
            
            # Simple patterns for task extraction
            task_patterns = [
                r'(?:please|kindly|could you|can you)\s+([^.!?]+[.!?])',
                r'(?:need to|must|should|have to)\s+([^.!?]+[.!?])',
                r'(?:todo|to-do|to do|action item|task):\s*([^.!?]+[.!?])',
                r'(?:deadline|due date|by):\s*([^.!?]+[.!?])'
            ]
            
            tasks = []
            for pattern in task_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    task_text = match.group(1).strip() if match.groups() else match.group(0).strip()
                    tasks.append({
                        "text": task_text,
                        "type": "task",
                        "priority": "medium",  # Default priority
                        "status": "pending"    # Default status
                    })
            
            self.logger.info(f"Extracted {len(tasks)} tasks")
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error extracting tasks: {str(e)}")
            return []
    
    def process_email(self, email_data: Dict) -> Dict:
        """
        Process an email to generate a summary and extract key information.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Dictionary with processed email data including summary and extractions
        """
        try:
            # Generate summary
            summary = self.generate_summary(email_data)
            
            # Combine subject and body for extraction
            subject = email_data.get("subject", "")
            body = email_data.get("body", "")
            full_text = f"{subject}\n\n{body}"
            
            # Extract key information
            dates_times = self.extract_dates_and_times(full_text)
            contacts = self.extract_contacts(full_text)
            tasks = self.extract_tasks(full_text)
            
            # Create processed email data
            processed_data = {
                "message_id": email_data.get("message_id", ""),
                "summary": summary,
                "extractions": {
                    "dates_times": dates_times,
                    "contacts": contacts,
                    "tasks": tasks
                },
                "processing_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed email with ID {email_data.get('message_id', '')}")
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing email: {str(e)}")
            
            # Return a minimal processed data in case of error
            return {
                "message_id": email_data.get("message_id", ""),
                "summary": "Failed to process email due to an error.",
                "extractions": {
                    "dates_times": [],
                    "contacts": [],
                    "tasks": []
                },
                "processing_timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def batch_process(self, emails: List[Dict]) -> List[Dict]:
        """
        Process a batch of emails.
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            List of processed email data
        """
        self.logger.info(f"Processing batch of {len(emails)} emails")
        
        results = []
        for email in emails:
            processed_data = self.process_email(email)
            
            # Combine the original email with its processed data
            processed_email = {
                **email,
                "processed_data": processed_data
            }
            
            results.append(processed_email)
        
        self.logger.info(f"Completed processing of {len(results)} emails")
        return results

# Example usage
def main():
    # Example configuration
    config = {
        "model_type": "gpt",
        "summary_max_length": 150
    }
    
    # Example email
    email = {
        "message_id": "<example123@mail.com>",
        "subject": "Meeting Next Tuesday",
        "from": "colleague@example.com",
        "to": "user@example.com",
        "body": "Hi there,\n\nCould you please join our team meeting next Tuesday at 2:30 PM? We'll be discussing the Q3 results and planning for Q4. Please prepare a short summary of your current projects.\n\nAlso, can you send me the contact details for Dr. John Smith? I need to reach him regarding the client presentation.\n\nThanks,\nMary\nPhone: (555) 123-4567"
    }
    
    # Initialize and use the summarization & extraction agent
    agent = SummarizationExtractionAgent(config)
    result = agent.process_email(email)
    
    print(f"Summary: {result['summary']}")
    print("\nExtracted dates and times:")
    for item in result['extractions']['dates_times']:
        print(f"  - {item['text']} ({item['type']})")
    
    print("\nExtracted contacts:")
    for item in result['extractions']['contacts']:
        print(f"  - {item['text']} ({item['type']})")
    
    print("\nExtracted tasks:")
    for item in result['extractions']['tasks']:
(Content truncated due to size limit. Use line ranges to read in chunks)