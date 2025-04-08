"""
Configuration module for the Reddit Automation Bot
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "health_wellness_bot v1.0.0")

# Target subreddits and keywords
DEFAULT_SUBREDDITS = [
    "health", "wellness", "alternativemedicine", "nutrition", 
    "supplements", "holistic", "naturalremedies"
]

DEFAULT_KEYWORDS = {
    "health": ["health", "healthy", "wellbeing", "doctor", "medical", "condition", "symptoms"],
    "wellness": ["wellness", "lifestyle", "holistic", "mindfulness", "self-care", "balance"],
    "alternative_medicine": ["natural", "remedy", "herbal", "alternative", "homeopathy", "acupuncture", "ayurveda"]
}

# Load custom configuration if available
try:
    with open('config.json', 'r') as f:
        custom_config = json.load(f)
        
    SUBREDDITS = custom_config.get('subreddits', DEFAULT_SUBREDDITS)
    KEYWORDS = custom_config.get('keywords', DEFAULT_KEYWORDS)
    
except (FileNotFoundError, json.JSONDecodeError):
    SUBREDDITS = DEFAULT_SUBREDDITS
    KEYWORDS = DEFAULT_KEYWORDS

# Post filters
MIN_POST_SCORE = int(os.getenv("MIN_POST_SCORE", "1"))  # Minimum score for post to be considered
MIN_POST_AGE_MINUTES = int(os.getenv("MIN_POST_AGE_MINUTES", "5"))  # Allow post to age before responding
MAX_POST_AGE_HOURS = int(os.getenv("MAX_POST_AGE_HOURS", "24"))  # Don't respond to posts older than this

# Scheduling settings
SCAN_INTERVAL_MINUTES = int(os.getenv("SCAN_INTERVAL_MINUTES", "15"))  # How often to scan for new posts
RESPONSE_DELAY_MINUTES = int(os.getenv("RESPONSE_DELAY_MINUTES", "2"))  # Random delay before posting
MAX_RESPONSES_PER_DAY = int(os.getenv("MAX_RESPONSES_PER_DAY", "20"))  # Limit total daily responses
MAX_RESPONSES_PER_SUBREDDIT = int(os.getenv("MAX_RESPONSES_PER_SUBREDDIT", "5"))  # Daily per subreddit

# Logging configuration
LOG_FILE = os.getenv("LOG_FILE", "bot_activity.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
JSON_LOG_FILE = os.getenv("JSON_LOG_FILE", "bot_activity.json")
CSV_LOG_FILE = os.getenv("CSV_LOG_FILE", "bot_activity.csv")

# Dashboard configuration
ENABLE_DASHBOARD = os.getenv("ENABLE_DASHBOARD", "True").lower() in ("true", "1", "yes")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "3000"))

# Database configuration (updated to use SQLite instead of PostgreSQL)
USE_SQLITE = True
SQLITE_DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reddit_bot.db')
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{SQLITE_DATABASE_PATH}")
