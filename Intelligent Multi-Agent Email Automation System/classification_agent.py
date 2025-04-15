"""
Classification Agent for the Intelligent Multi-Agent Email Automation System.

This agent utilizes NLP models to accurately categorize incoming emails into 
predefined classes (important, support, promotional, spam, etc.).
"""

import logging
from typing import Dict, List, Optional, Union
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ClassificationAgent:
    """
    Agent responsible for classifying emails into different categories.
    
    This agent uses NLP models to analyze email content and metadata
    to categorize emails into predefined classes.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Classification Agent.
        
        Args:
            config: Configuration dictionary containing model settings and categories
        """
        self.config = config
        self.categories = config.get("categories", ["important", "promotional", "support", "spam", "other"])
        self.model_type = config.get("model_type", "bert")
        self.model = None
        self.logger = logger
        
        # Initialize the model
        self._initialize_model()
        
    def _initialize_model(self):
        """
        Initialize the NLP model for classification.
        
        This is a placeholder for actual model initialization.
        In a real implementation, this would load a pre-trained model.
        """
        self.logger.info(f"Initializing {self.model_type} model for classification")
        
        # Placeholder for model initialization
        # In a real implementation, this would use transformers library to load a BERT model
        # Example:
        # from transformers import AutoTokenizer, AutoModelForSequenceClassification
        # self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        # self.model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=len(self.categories))
        
        self.logger.info("Model initialized successfully")
    
    def preprocess_email(self, email_data: Dict) -> Dict:
        """
        Preprocess email data for classification.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Preprocessed email data
        """
        # Extract relevant features for classification
        features = {
            "subject": email_data.get("subject", ""),
            "body": email_data.get("body", ""),
            "sender": email_data.get("from", ""),
            "recipient": email_data.get("to", ""),
            "has_attachments": len(email_data.get("attachments", [])) > 0
        }
        
        # Additional preprocessing steps could include:
        # - Text normalization
        # - Removing stopwords
        # - Tokenization
        # - Feature extraction
        
        return features
    
    def classify_email(self, email_data: Dict) -> Dict:
        """
        Classify an email into one of the predefined categories.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Dictionary with classification results
        """
        try:
            # Preprocess the email
            features = self.preprocess_email(email_data)
            
            # This is a placeholder for actual classification logic
            # In a real implementation, this would use the loaded model to predict the category
            
            # Simulate classification with random probabilities
            # In a real implementation, this would be the output of the model
            probabilities = np.random.dirichlet(np.ones(len(self.categories)), size=1)[0]
            
            # Get the predicted category
            predicted_category = self.categories[np.argmax(probabilities)]
            
            # Create classification result
            classification_result = {
                "message_id": email_data.get("message_id", ""),
                "predicted_category": predicted_category,
                "confidence": float(max(probabilities)),
                "category_probabilities": {
                    category: float(prob) for category, prob in zip(self.categories, probabilities)
                },
                "features_used": list(features.keys())
            }
            
            self.logger.info(f"Classified email as '{predicted_category}' with confidence {classification_result['confidence']:.2f}")
            
            return classification_result
            
        except Exception as e:
            self.logger.error(f"Error classifying email: {str(e)}")
            
            # Return a default classification in case of error
            return {
                "message_id": email_data.get("message_id", ""),
                "predicted_category": "other",
                "confidence": 0.0,
                "category_probabilities": {category: 0.0 for category in self.categories},
                "features_used": [],
                "error": str(e)
            }
    
    def batch_classify(self, emails: List[Dict]) -> List[Dict]:
        """
        Classify a batch of emails.
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            List of classification results
        """
        self.logger.info(f"Classifying batch of {len(emails)} emails")
        
        results = []
        for email in emails:
            classification = self.classify_email(email)
            
            # Combine the original email with its classification
            classified_email = {
                **email,
                "classification": classification
            }
            
            results.append(classified_email)
        
        self.logger.info(f"Completed classification of {len(results)} emails")
        return results

# Example usage
def main():
    # Example configuration
    config = {
        "categories": ["important", "promotional", "support", "spam", "other"],
        "model_type": "bert",
        "threshold": 0.7
    }
    
    # Example email
    email = {
        "message_id": "<example123@mail.com>",
        "subject": "Your Account Statement",
        "from": "bank@example.com",
        "to": "user@example.com",
        "body": "Please find attached your monthly account statement.",
        "attachments": [{"filename": "statement.pdf"}]
    }
    
    # Initialize and use the classification agent
    agent = ClassificationAgent(config)
    result = agent.classify_email(email)
    
    print(f"Email classified as: {result['predicted_category']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print("Category probabilities:")
    for category, prob in result['category_probabilities'].items():
        print(f"  {category}: {prob:.2f}")

if __name__ == "__main__":
    main()
