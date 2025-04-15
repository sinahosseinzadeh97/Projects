"""
Response Generation Agent for the Intelligent Multi-Agent Email Automation System.

This agent creates intelligent and context-aware reply drafts for emails,
providing both auto-send and review options for the generated responses.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResponseGenerationAgent:
    """
    Agent responsible for generating email responses.
    
    This agent uses NLP models to create context-aware reply drafts
    based on the content and classification of incoming emails.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Response Generation Agent.
        
        Args:
            config: Configuration dictionary containing model settings and templates
        """
        self.config = config
        self.model_type = config.get("model_type", "gpt")
        self.templates = config.get("templates", {})
        self.auto_send_threshold = config.get("auto_send_threshold", 0.9)
        self.model = None
        self.logger = logger
        
        # Initialize the model
        self._initialize_model()
        
    def _initialize_model(self):
        """
        Initialize the NLP model for response generation.
        
        This is a placeholder for actual model initialization.
        In a real implementation, this would load a pre-trained model.
        """
        self.logger.info(f"Initializing {self.model_type} model for response generation")
        
        # Placeholder for model initialization
        # In a real implementation, this would use a library like transformers to load a model
        # Example:
        # from transformers import AutoTokenizer, AutoModelForCausalLM
        # self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        # self.model = AutoModelForCausalLM.from_pretrained("gpt2")
        
        self.logger.info("Model initialized successfully")
    
    def _get_template(self, category: str) -> str:
        """
        Get a response template based on email category.
        
        Args:
            category: Email category (e.g., important, promotional, support)
            
        Returns:
            Template string for the specified category
        """
        # Default templates for different categories
        default_templates = {
            "important": "Thank you for your important message. I've reviewed it and {summary}. I'll {action} as requested.",
            "support": "Thank you for reaching out to our support team. I understand that {summary}. We'll {action} to resolve this issue.",
            "promotional": "Thank you for sharing this offer. I'll review the details about {summary} and get back to you if interested.",
            "spam": "",  # No response for spam
            "other": "Thank you for your message. I've noted that {summary}. I'll get back to you soon."
        }
        
        # Get template from config or use default
        return self.templates.get(category, default_templates.get(category, default_templates["other"]))
    
    def _extract_key_info(self, email_data: Dict) -> Dict:
        """
        Extract key information from email data for response generation.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Dictionary with key information for response generation
        """
        # Extract basic email information
        info = {
            "sender_name": "",
            "sender_email": "",
            "subject": email_data.get("subject", ""),
            "summary": "",
            "action_items": [],
            "dates_times": [],
            "category": "other"
        }
        
        # Extract sender information
        from_field = email_data.get("from", "")
        if "<" in from_field and ">" in from_field:
            # Format: "Name <email@example.com>"
            parts = from_field.split("<", 1)
            info["sender_name"] = parts[0].strip()
            info["sender_email"] = parts[1].split(">", 1)[0].strip()
        else:
            # Just email address
            info["sender_email"] = from_field.strip()
            info["sender_name"] = from_field.split("@", 1)[0] if "@" in from_field else from_field
        
        # Extract classification if available
        if "classification" in email_data:
            info["category"] = email_data["classification"].get("predicted_category", "other")
        
        # Extract processed data if available
        if "processed_data" in email_data:
            processed_data = email_data["processed_data"]
            
            # Get summary
            info["summary"] = processed_data.get("summary", "")
            
            # Get action items/tasks
            if "extractions" in processed_data:
                extractions = processed_data["extractions"]
                
                # Get tasks
                if "tasks" in extractions:
                    info["action_items"] = [task.get("text", "") for task in extractions.get("tasks", [])]
                
                # Get dates and times
                if "dates_times" in extractions:
                    info["dates_times"] = [dt.get("text", "") for dt in extractions.get("dates_times", [])]
        
        return info
    
    def generate_response(self, email_data: Dict) -> Dict:
        """
        Generate a response for an email.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Dictionary with generated response data
        """
        try:
            # Extract key information
            info = self._extract_key_info(email_data)
            
            # Skip response generation for spam
            if info["category"] == "spam":
                self.logger.info("Skipping response generation for spam email")
                return {
                    "message_id": email_data.get("message_id", ""),
                    "response_text": "",
                    "auto_send": False,
                    "confidence": 0.0,
                    "generation_timestamp": datetime.now().isoformat()
                }
            
            # Get template for the category
            template = self._get_template(info["category"])
            
            # This is a placeholder for actual response generation logic
            # In a real implementation, this would use the loaded model to generate a response
            
            # Simple template-based response as a placeholder
            # In a real implementation, this would be replaced with model-generated response
            
            # Prepare template variables
            template_vars = {
                "summary": info["summary"] or "your message",
                "action": "take appropriate action" if info["action_items"] else "follow up"
            }
            
            # Generate response text
            response_text = template.format(**template_vars)
            
            # Add greeting
            greeting = f"Hello {info['sender_name']}," if info["sender_name"] else "Hello,"
            response_text = f"{greeting}\n\n{response_text}"
            
            # Add action items if any
            if info["action_items"]:
                response_text += "\n\nRegarding your requests:"
                for item in info["action_items"][:3]:  # Limit to first 3 items
                    response_text += f"\n- I'll {item.lower() if item.lower().startswith('please ') else item}"
            
            # Add date/time acknowledgment if any
            if info["dates_times"]:
                date_time_str = ", ".join(info["dates_times"][:2])  # Limit to first 2 dates/times
                response_text += f"\n\nI've noted the date/time: {date_time_str}."
            
            # Add signature
            response_text += "\n\nBest regards,\n[Your Name]"
            
            # Determine confidence and auto-send recommendation
            # In a real implementation, this would be based on model confidence
            confidence = 0.85 if info["category"] in ["important", "support"] else 0.7
            auto_send = confidence >= self.auto_send_threshold
            
            response_data = {
                "message_id": email_data.get("message_id", ""),
                "response_text": response_text,
                "auto_send": auto_send,
                "confidence": confidence,
                "category": info["category"],
                "generation_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Generated response for email with ID {email_data.get('message_id', '')}")
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            
            # Return a minimal response data in case of error
            return {
                "message_id": email_data.get("message_id", ""),
                "response_text": "I've received your email and will get back to you soon.",
                "auto_send": False,
                "confidence": 0.0,
                "generation_timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def batch_generate(self, emails: List[Dict]) -> List[Dict]:
        """
        Generate responses for a batch of emails.
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            List of emails with generated responses
        """
        self.logger.info(f"Generating responses for batch of {len(emails)} emails")
        
        results = []
        for email in emails:
            response_data = self.generate_response(email)
            
            # Combine the original email with its response data
            email_with_response = {
                **email,
                "response_data": response_data
            }
            
            results.append(email_with_response)
        
        self.logger.info(f"Completed response generation for {len(results)} emails")
        return results

# Example usage
def main():
    # Example configuration
    config = {
        "model_type": "gpt",
        "auto_send_threshold": 0.9,
        "templates": {
            "important": "Thank you for your important message. I've reviewed it and {summary}. I'll {action} as soon as possible.",
            "support": "Thank you for contacting our support team. I understand that {summary}. We'll {action} to address your concerns."
        }
    }
    
    # Example email with processed data
    email = {
        "message_id": "<example123@mail.com>",
        "subject": "Meeting Next Tuesday",
        "from": "John Smith <john.smith@example.com>",
        "to": "user@example.com",
        "body": "Hi there,\n\nCould you please join our team meeting next Tuesday at 2:30 PM? We'll be discussing the Q3 results and planning for Q4. Please prepare a short summary of your current projects.\n\nThanks,\nJohn",
        "classification": {
            "predicted_category": "important",
            "confidence": 0.92
        },
        "processed_data": {
            "summary": "John is inviting you to a team meeting next Tuesday at 2:30 PM to discuss Q3 results and Q4 planning",
            "extractions": {
                "tasks": [
                    {"text": "join team meeting next Tuesday"},
                    {"text": "prepare a short summary of current projects"}
                ],
                "dates_times": [
                    {"text": "next Tuesday at 2:30 PM", "type": "datetime"}
                ]
            }
        }
    }
    
    # Initialize and use the response generation agent
    agent = ResponseGenerationAgent(config)
    result = agent.generate_response(email)
    
    print("Generated Response:")
    print("-" * 50)
    print(result["response_text"])
    print("-" * 50)
    print(f"Auto-send: {result['auto_send']}")
    print(f"Confidence: {result['confidence']:.2f}")

if __name__ == "__main__":
    main()
