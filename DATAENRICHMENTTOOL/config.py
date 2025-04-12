"""
Configuration module for API keys and settings.

This module provides secure handling of API keys and configuration settings
for the data processing tool.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import dotenv

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

class Config:
    """
    Configuration manager for the application.
    
    This class handles loading and accessing configuration settings,
    including API keys, from environment variables or a config file.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (str, optional): Path to configuration file
        """
        self.config_file = config_file
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """
        Load configuration from environment variables and config file.
        """
        # Load from environment variables first
        self.config = {
            'openai': {
                'api_key': os.environ.get('OPEN_AI_API_KEY', '')
            },
            'google': {
                'api_key': os.environ.get('GOOGLE_API_KEY', '')
            },
            'huggingface': {
                'api_key': os.environ.get('HUGGING_FACE_API_KEY', '') or os.environ.get('HUGGIG_FACE', '')
            },
            'database': {
                'path': os.environ.get('DATABASE_PATH', 'data/product_database.db')
            }
        }
        
        # Load from config file if provided
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                
                # Update config with file values
                for section, values in file_config.items():
                    if section not in self.config:
                        self.config[section] = {}
                    
                    if isinstance(values, dict):
                        self.config[section].update(values)
                    else:
                        self.config[section] = values
            except Exception as e:
                print(f"Error loading config file: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            default (any, optional): Default value if not found
            
        Returns:
            any: Configuration value
        """
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default
    
    def set(self, section: str, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            value (any): Configuration value
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def save(self, config_file: Optional[str] = None):
        """
        Save configuration to a file.
        
        Args:
            config_file (str, optional): Path to configuration file
        """
        file_path = config_file or self.config_file
        if not file_path:
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def has_api_keys(self) -> bool:
        """
        Check if all API keys are available.
        
        Returns:
            bool: True if all API keys are available
        """
        return (
            bool(self.get('openai', 'api_key')) and
            bool(self.get('google', 'api_key')) and
            bool(self.get('huggingface', 'api_key'))
        )

# Create a global configuration instance
config = Config()

# Set API keys from environment variables if available
if os.environ.get('OPEN_AI_API_KEY'):
    config.set('openai', 'api_key', os.environ.get('OPEN_AI_API_KEY'))

if os.environ.get('GOOGLE_API_KEY'):
    config.set('google', 'api_key', os.environ.get('GOOGLE_API_KEY'))

if os.environ.get('HUGGING_FACE_API_KEY') or os.environ.get('HUGGIG_FACE'):
    config.set('huggingface', 'api_key', os.environ.get('HUGGING_FACE_API_KEY') or os.environ.get('HUGGIG_FACE'))
