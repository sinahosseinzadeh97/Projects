"""
Configuration module for the Intelligent Multi-Agent Email Automation System.
This file handles loading and managing configuration settings.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default configuration paths
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "default_config.json")
USER_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "user_config.json")

class Config:
    """Configuration manager for the email automation system."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Optional path to a configuration file
        """
        self.config = {}
        self.config_path = config_path
        self.logger = logger
        
        # Load default configuration
        self._load_default_config()
        
        # Load user configuration if available
        self._load_user_config()
        
        # Load specified configuration if provided
        if config_path:
            self._load_config(config_path)
    
    def _load_default_config(self):
        """Load the default configuration."""
        try:
            # Create default config if it doesn't exist
            if not os.path.exists(DEFAULT_CONFIG_PATH):
                os.makedirs(os.path.dirname(DEFAULT_CONFIG_PATH), exist_ok=True)
                
                # Default configuration
                default_config = {
                    "database": {
                        "mongodb_url": "mongodb://localhost:27017",
                        "database_name": "email_automation"
                    },
                    "cache": {
                        "redis_host": "localhost",
                        "redis_port": 6379,
                        "redis_db": 0
                    },
                    "api": {
                        "host": "0.0.0.0",
                        "port": 8000,
                        "debug": True,
                        "cors_origins": ["*"]
                    },
                    "email_ingestion": {
                        "batch_size": 10,
                        "polling_interval": 300  # 5 minutes
                    },
                    "classification": {
                        "model_type": "bert",
                        "categories": ["important", "promotional", "support", "spam", "other"],
                        "threshold": 0.7
                    },
                    "summarization": {
                        "model_type": "gpt",
                        "summary_max_length": 150
                    },
                    "response_generation": {
                        "model_type": "gpt",
                        "auto_send_threshold": 0.9,
                        "templates": {
                            "important": "Thank you for your important message. I've reviewed it and {summary}. I'll {action} as requested.",
                            "support": "Thank you for reaching out to our support team. I understand that {summary}. We'll {action} to resolve this issue.",
                            "promotional": "Thank you for sharing this offer. I'll review the details about {summary} and get back to you if interested.",
                            "spam": "",
                            "other": "Thank you for your message. I've noted that {summary}. I'll get back to you soon."
                        }
                    },
                    "integration": {
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
                    },
                    "logging": {
                        "level": "INFO",
                        "file": "logs/email_automation.log",
                        "max_size": 10485760,  # 10 MB
                        "backup_count": 5
                    }
                }
                
                # Write default configuration
                with open(DEFAULT_CONFIG_PATH, "w") as f:
                    json.dump(default_config, f, indent=4)
                
                self.logger.info(f"Created default configuration at {DEFAULT_CONFIG_PATH}")
            
            # Load default configuration
            with open(DEFAULT_CONFIG_PATH, "r") as f:
                self.config = json.load(f)
            
            self.logger.info(f"Loaded default configuration from {DEFAULT_CONFIG_PATH}")
            
        except Exception as e:
            self.logger.error(f"Error loading default configuration: {str(e)}")
    
    def _load_user_config(self):
        """Load the user configuration if available."""
        try:
            if os.path.exists(USER_CONFIG_PATH):
                with open(USER_CONFIG_PATH, "r") as f:
                    user_config = json.load(f)
                
                # Update configuration with user settings
                self._update_config(user_config)
                
                self.logger.info(f"Loaded user configuration from {USER_CONFIG_PATH}")
            
        except Exception as e:
            self.logger.error(f"Error loading user configuration: {str(e)}")
    
    def _load_config(self, config_path: str):
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                
                # Update configuration with loaded settings
                self._update_config(config)
                
                self.logger.info(f"Loaded configuration from {config_path}")
            else:
                self.logger.warning(f"Configuration file not found: {config_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading configuration from {config_path}: {str(e)}")
    
    def _update_config(self, new_config: Dict):
        """
        Update configuration with new settings.
        
        Args:
            new_config: New configuration dictionary
        """
        # Recursively update configuration
        def update_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    d[k] = update_dict(d[k], v)
                else:
                    d[k] = v
            return d
        
        self.config = update_dict(self.config, new_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            # Split key by dots
            parts = key.split(".")
            
            # Navigate through configuration
            value = self.config
            for part in parts:
                value = value[part]
            
            return value
            
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Configuration value
            
        Returns:
            True if set was successful, False otherwise
        """
        try:
            # Split key by dots
            parts = key.split(".")
            
            # Navigate through configuration
            config = self.config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            
            # Set value
            config[parts[-1]] = value
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting configuration value for {key}: {str(e)}")
            return False
    
    def save_user_config(self) -> bool:
        """
        Save the current configuration as user configuration.
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(USER_CONFIG_PATH), exist_ok=True)
            
            # Write configuration
            with open(USER_CONFIG_PATH, "w") as f:
                json.dump(self.config, f, indent=4)
            
            self.logger.info(f"Saved user configuration to {USER_CONFIG_PATH}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving user configuration: {str(e)}")
            return False
    
    def save_config(self, config_path: str) -> bool:
        """
        Save the current configuration to a file.
        
        Args:
            config_path: Path to save the configuration
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Write configuration
            with open(config_path, "w") as f:
                json.dump(self.config, f, indent=4)
            
            self.logger.info(f"Saved configuration to {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration to {config_path}: {str(e)}")
            return False
    
    def get_all(self) -> Dict:
        """
        Get the entire configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()

# Create configuration instance
config = Config()

# Example usage
def main():
    # Get configuration values
    mongodb_url = config.get("database.mongodb_url")
    redis_host = config.get("cache.redis_host")
    api_port = config.get("api.port")
    
    print(f"MongoDB URL: {mongodb_url}")
    print(f"Redis Host: {redis_host}")
    print(f"API Port: {api_port}")
    
    # Set a configuration value
    config.set("api.debug", False)
    
    # Save configuration
    config.save_user_config()

if __name__ == "__main__":
    main()
