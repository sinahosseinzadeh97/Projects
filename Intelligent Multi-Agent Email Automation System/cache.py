"""
Redis cache configuration for the Intelligent Multi-Agent Email Automation System.
This file sets up the Redis connection and provides caching functions.
"""

import redis
import json
import logging
from typing import Dict, List, Optional, Any, Union
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis connection settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Cache key prefixes
EMAIL_PREFIX = "email:"
PROVIDER_PREFIX = "provider:"
TEMPLATE_PREFIX = "template:"
SETTINGS_PREFIX = "settings:"
SESSION_PREFIX = "session:"

# Default expiration times (in seconds)
DEFAULT_EXPIRATION = 3600  # 1 hour
SESSION_EXPIRATION = 1800  # 30 minutes

class Cache:
    """Cache class for Redis operations."""
    
    def __init__(self):
        """Initialize the Redis connection."""
        self.redis = None
        self.logger = logger
        
    def connect(self):
        """Connect to Redis."""
        try:
            # Create Redis client
            self.redis = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
            
            # Verify connection
            self.redis.ping()
            
            self.logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
            return True
            
        except redis.ConnectionError as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            return False
    
    def close(self):
        """Close the Redis connection."""
        if self.redis:
            self.redis.close()
            self.logger.info("Closed Redis connection")
    
    def set(self, key: str, value: Union[str, Dict, List], expiration: int = DEFAULT_EXPIRATION) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache (string, dict, or list)
            expiration: Expiration time in seconds
            
        Returns:
            True if set was successful, False otherwise
        """
        try:
            # Convert dict/list to JSON string
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            # Set value
            self.redis.set(key, value, ex=expiration)
            
            self.logger.debug(f"Set cache key: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting cache key {key}: {str(e)}")
            return False
    
    def get(self, key: str, as_json: bool = False) -> Optional[Union[str, Dict, List]]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            as_json: Whether to parse the value as JSON
            
        Returns:
            Cached value or None if not found
        """
        try:
            # Get value
            value = self.redis.get(key)
            
            if value is None:
                return None
            
            # Parse JSON if requested
            if as_json:
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    self.logger.warning(f"Failed to parse JSON for key {key}")
            
            self.logger.debug(f"Got cache key: {key}")
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting cache key {key}: {str(e)}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if delete was successful, False otherwise
        """
        try:
            # Delete value
            self.redis.delete(key)
            
            self.logger.debug(f"Deleted cache key: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting cache key {key}: {str(e)}")
            return False
    
    def cache_email(self, email_id: str, email_data: Dict, expiration: int = DEFAULT_EXPIRATION) -> bool:
        """
        Cache email data.
        
        Args:
            email_id: Email ID
            email_data: Email data dictionary
            expiration: Expiration time in seconds
            
        Returns:
            True if cache was successful, False otherwise
        """
        key = f"{EMAIL_PREFIX}{email_id}"
        return self.set(key, email_data, expiration)
    
    def get_cached_email(self, email_id: str) -> Optional[Dict]:
        """
        Get cached email data.
        
        Args:
            email_id: Email ID
            
        Returns:
            Cached email data or None if not found
        """
        key = f"{EMAIL_PREFIX}{email_id}"
        return self.get(key, as_json=True)
    
    def cache_provider(self, provider_id: str, provider_data: Dict, expiration: int = DEFAULT_EXPIRATION) -> bool:
        """
        Cache provider data.
        
        Args:
            provider_id: Provider ID
            provider_data: Provider data dictionary
            expiration: Expiration time in seconds
            
        Returns:
            True if cache was successful, False otherwise
        """
        key = f"{PROVIDER_PREFIX}{provider_id}"
        return self.set(key, provider_data, expiration)
    
    def get_cached_provider(self, provider_id: str) -> Optional[Dict]:
        """
        Get cached provider data.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Cached provider data or None if not found
        """
        key = f"{PROVIDER_PREFIX}{provider_id}"
        return self.get(key, as_json=True)
    
    def cache_template(self, template_id: str, template_data: Dict, expiration: int = DEFAULT_EXPIRATION) -> bool:
        """
        Cache template data.
        
        Args:
            template_id: Template ID
            template_data: Template data dictionary
            expiration: Expiration time in seconds
            
        Returns:
            True if cache was successful, False otherwise
        """
        key = f"{TEMPLATE_PREFIX}{template_id}"
        return self.set(key, template_data, expiration)
    
    def get_cached_template(self, template_id: str) -> Optional[Dict]:
        """
        Get cached template data.
        
        Args:
            template_id: Template ID
            
        Returns:
            Cached template data or None if not found
        """
        key = f"{TEMPLATE_PREFIX}{template_id}"
        return self.get(key, as_json=True)
    
    def cache_settings(self, settings_data: Dict, expiration: int = DEFAULT_EXPIRATION) -> bool:
        """
        Cache settings data.
        
        Args:
            settings_data: Settings data dictionary
            expiration: Expiration time in seconds
            
        Returns:
            True if cache was successful, False otherwise
        """
        key = f"{SETTINGS_PREFIX}system"
        return self.set(key, settings_data, expiration)
    
    def get_cached_settings(self) -> Optional[Dict]:
        """
        Get cached settings data.
        
        Returns:
            Cached settings data or None if not found
        """
        key = f"{SETTINGS_PREFIX}system"
        return self.get(key, as_json=True)
    
    def create_session(self, session_id: str, session_data: Dict, expiration: int = SESSION_EXPIRATION) -> bool:
        """
        Create a new session.
        
        Args:
            session_id: Session ID
            session_data: Session data dictionary
            expiration: Expiration time in seconds
            
        Returns:
            True if session creation was successful, False otherwise
        """
        key = f"{SESSION_PREFIX}{session_id}"
        return self.set(key, session_data, expiration)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        key = f"{SESSION_PREFIX}{session_id}"
        return self.get(key, as_json=True)
    
    def update_session(self, session_id: str, session_data: Dict, expiration: int = SESSION_EXPIRATION) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session ID
            session_data: Session data dictionary
            expiration: Expiration time in seconds
            
        Returns:
            True if session update was successful, False otherwise
        """
        key = f"{SESSION_PREFIX}{session_id}"
        return self.set(key, session_data, expiration)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session deletion was successful, False otherwise
        """
        key = f"{SESSION_PREFIX}{session_id}"
        return self.delete(key)

# Create cache instance
cache = Cache()

# Example usage
def main():
    # Connect to Redis
    cache.connect()
    
    # Example email
    email_data = {
        "message_id": "<example123@mail.com>",
        "subject": "Test Email",
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "body": "This is a test email.",
        "timestamp": datetime.now().isoformat()
    }
    
    # Cache email
    email_id = "123456"
    cache.cache_email(email_id, email_data)
    print(f"Cached email with ID: {email_id}")
    
    # Get cached email
    cached_email = cache.get_cached_email(email_id)
    print(f"Retrieved cached email: {cached_email}")
    
    # Close connection
    cache.close()

if __name__ == "__main__":
    main()
