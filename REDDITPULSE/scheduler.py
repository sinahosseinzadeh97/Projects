"""
Scheduler module to manage the timing of bot actions
"""
import logging
import time
import random
from datetime import datetime, timedelta
import schedule

class BotScheduler:
    """Manages scheduling and timing of bot actions"""
    
    def __init__(self, scan_interval_minutes=15, response_delay_range=(1, 5)):
        """
        Initialize the scheduler
        
        Args:
            scan_interval_minutes (int): How often to scan for new posts
            response_delay_range (tuple): Range of minutes to randomly delay responses
        """
        self.logger = logging.getLogger(__name__)
        self.scan_interval = scan_interval_minutes
        self.min_delay, self.max_delay = response_delay_range
        
        self.schedule = schedule
        self.logger.info(f"Scheduler initialized with {scan_interval_minutes} minute intervals")
    
    def add_scan_job(self, scan_function):
        """
        Add a recurring job to scan for new posts
        
        Args:
            scan_function (callable): Function to call for scanning
        """
        self.schedule.every(self.scan_interval).minutes.do(scan_function)
        self.logger.info(f"Added scheduled scan every {self.scan_interval} minutes")
    
    def get_response_delay(self):
        """
        Get a random delay time for posting responses to appear more human-like
        
        Returns:
            int: Delay in seconds
        """
        delay_minutes = random.uniform(self.min_delay, self.max_delay)
        delay_seconds = int(delay_minutes * 60)
        return delay_seconds
    
    def run(self):
        """Run the scheduler indefinitely"""
        self.logger.info("Starting scheduler")
        
        while True:
            self.schedule.run_pending()
            time.sleep(1)
    
    def is_active_time(self):
        """
        Check if current time is appropriate for posting
        (e.g., avoid very late night posting to seem more human)
        
        Returns:
            bool: True if it's an active time, False otherwise
        """
        now = datetime.now()
        
        # Example: only active between 7 AM and 11 PM
        if now.hour >= 7 and now.hour < 23:
            return True
        
        return False
