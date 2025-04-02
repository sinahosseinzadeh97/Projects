"""
Configuration module for the AI research system.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# LLM configuration
DEFAULT_LLM_PROVIDER = "openai"
DEFAULT_LLM_MODEL = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                            # do not change this unless explicitly requested by the user

# Agent configurations
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30  # seconds

# Caching configuration
CACHE_ENABLED = True
CACHE_EXPIRY = 3600  # seconds (1 hour)

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 20

# Confidence thresholds
MIN_CONFIDENCE_THRESHOLD = 0.6
