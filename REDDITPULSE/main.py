"""
Main entry point for the Reddit Automation Bot
This module initializes and runs the bot with a web dashboard.
"""
import time
import logging
import threading
import schedule
import os
import sqlite3
from reddit_bot import RedditBot
from dashboard import app
import config
from post_analyzer import PostAnalyzer
from response_generator import ResponseGenerator
from test_mode import SimulatedTester

# Create logs directory
import os
logs_dir = "logs"
os.makedirs(logs_dir, exist_ok=True)

# Set up log file path
log_file = config.LOG_FILE
if not os.path.dirname(log_file):
    log_file = os.path.join(logs_dir, log_file)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_file
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

# Initialize SQLite database if using SQLite
def initialize_sqlite_db():
    """Initialize SQLite database with required tables"""
    if config.USE_SQLITE:
        logger.info(f"Initializing SQLite database at {config.SQLITE_DATABASE_PATH}")
        try:
            # Extract database path from SQLite URL
            db_path = config.SQLITE_DATABASE_PATH
            
            # Create connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables for storing bot activity and performance data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    post_id TEXT NOT NULL,
                    post_title TEXT NOT NULL,
                    subreddit TEXT NOT NULL,
                    comment_id TEXT,
                    relevance_score REAL NOT NULL,
                    keywords TEXT NOT NULL,
                    status TEXT NOT NULL,
                    template_id TEXT,
                    variant TEXT,
                    error TEXT
                )
            ''')
            
            # Create table for storing bot configuration
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            logger.info("SQLite database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {str(e)}", exc_info=True)
            raise

# Run test mode to generate sample data for the dashboard
tester = SimulatedTester()
analyzer = PostAnalyzer(config.KEYWORDS)
response_generator = ResponseGenerator()
tester.run_test(analyzer, response_generator)

def run_bot():
    """Initialize and run the Reddit bot."""
    logger.info("Starting Reddit Automation Bot")
    
    try:
        bot = RedditBot()
        
        # Schedule periodic scanning
        schedule.every(config.SCAN_INTERVAL_MINUTES).minutes.do(bot.run_cycle)
        
        # Run the initial cycle immediately
        bot.run_cycle()
        
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Bot terminated by user.")
    except Exception as e:
        logger.error(f"Bot failed with error: {str(e)}", exc_info=True)

def run_dashboard():
    """Run the web dashboard for monitoring if enabled."""
    if config.ENABLE_DASHBOARD:
        logger.debug(f"Starting dashboard with port 3000")
        app.run(host="0.0.0.0", port=3000, debug=True)

def run_test_mode():
    """Run the bot in test mode for demonstration purposes"""
    logger.info("Starting Reddit Bot in test/demo mode")
    
    try:
        # Initialize components
        analyzer = PostAnalyzer(config.KEYWORDS)
        response_generator = ResponseGenerator()
        tester = SimulatedTester()
        
        # Run the simulated test
        tester.run_test(analyzer, response_generator)
        
    except Exception as e:
        logger.error(f"Test mode failed with error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    logger.info("Initializing Reddit Automation Tool")
    
    # Initialize database if using SQLite
    if config.USE_SQLITE:
        initialize_sqlite_db()
    
    # Check if we should use test mode (when Reddit API isn't working)
    use_test_mode = True
    
    if use_test_mode:
        # Run in test/demo mode
        run_test_mode()
        
        # Run the dashboard in the main thread after test mode
        if config.ENABLE_DASHBOARD:
            logger.info(f"Starting dashboard on port 3000")
            app.run(host="0.0.0.0", port=3000, debug=True)
    else:
        # Start dashboard in a separate thread
        if config.ENABLE_DASHBOARD:
            dashboard_thread = threading.Thread(target=run_dashboard)
            dashboard_thread.daemon = True
            dashboard_thread.start()
            logger.info(f"Dashboard started on port 3000")
            
        # Run the bot in the main thread with real Reddit API
        run_bot()
