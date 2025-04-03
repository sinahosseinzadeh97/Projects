"""
Reddit Bot main class that coordinates all components
"""
import logging
import time
import random
from datetime import datetime, timedelta
import prawcore
from subreddit_monitor import SubredditMonitor
from post_analyzer import PostAnalyzer
from response_generator import ResponseGenerator
from logger import ActivityLogger
import config

class RedditBot:
    """Main bot class that coordinates monitoring, analysis and responding"""
    
    def __init__(self):
        """Initialize the bot and its components"""
        self.logger = logging.getLogger(__name__)
        self.activity_logger = ActivityLogger()
        
        # Initialize components
        self.monitor = SubredditMonitor(config.SUBREDDITS)
        self.analyzer = PostAnalyzer(config.KEYWORDS)
        self.response_gen = ResponseGenerator()
        
        # Tracking variables
        self.responses_today = 0
        self.subreddit_responses = {subreddit: 0 for subreddit in config.SUBREDDITS}
        self.last_reset_date = datetime.now().date()
        
        self.logger.info(f"Bot initialized with {len(config.SUBREDDITS)} subreddits")

    def reset_daily_counters(self):
        """Reset the daily response counters if it's a new day"""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.responses_today = 0
            self.subreddit_responses = {subreddit: 0 for subreddit in config.SUBREDDITS}
            self.last_reset_date = today
            self.logger.info("Daily response counters reset")

    def can_respond(self, subreddit):
        """Check if we haven't exceeded our daily response limits"""
        self.reset_daily_counters()
        
        if self.responses_today >= config.MAX_RESPONSES_PER_DAY:
            self.logger.info("Daily response limit reached")
            return False
        
        if self.subreddit_responses.get(subreddit, 0) >= config.MAX_RESPONSES_PER_SUBREDDIT:
            self.logger.info(f"Daily limit for subreddit r/{subreddit} reached")
            return False
        
        return True

    def run_cycle(self):
        """Run a complete bot cycle (monitor, analyze, respond)"""
        self.logger.info("Starting bot cycle")
        try:
            # Get new posts from target subreddits
            posts = self.monitor.get_new_posts()
            self.logger.info(f"Found {len(posts)} new posts to analyze")
            
            # Analyze posts for relevance
            relevant_posts = []
            for post in posts:
                relevance_score, matched_keywords = self.analyzer.analyze_post(post)
                
                # Filter posts based on relevance and post criteria
                post_age_minutes = (datetime.now() - datetime.fromtimestamp(post.created_utc)).total_seconds() / 60
                
                if (relevance_score > 0 and 
                    post.score >= config.MIN_POST_SCORE and
                    post_age_minutes >= config.MIN_POST_AGE_MINUTES and
                    post_age_minutes <= config.MAX_POST_AGE_HOURS * 60):
                    
                    post_data = {
                        'post': post,
                        'relevance_score': relevance_score,
                        'matched_keywords': matched_keywords,
                        'subreddit': post.subreddit.display_name.lower()
                    }
                    relevant_posts.append(post_data)
                    
            # Sort by relevance score
            relevant_posts.sort(key=lambda x: x['relevance_score'], reverse=True)
            self.logger.info(f"Found {len(relevant_posts)} relevant posts to respond to")
            
            # Generate and post responses
            for post_data in relevant_posts:
                post = post_data['post']
                subreddit = post_data['subreddit']
                
                # Check if we can respond (based on daily limits)
                if not self.can_respond(subreddit):
                    continue
                
                # Generate a response
                response_text = self.response_gen.generate_response(
                    post.title, 
                    post.selftext, 
                    post_data['matched_keywords']
                )
                
                if response_text:
                    # Add a random delay before posting to appear more human-like
                    delay = random.randint(1, config.RESPONSE_DELAY_MINUTES * 60)
                    self.logger.info(f"Waiting for {delay} seconds before responding")
                    time.sleep(delay)
                    
                    try:
                        # Post the response
                        comment = post.reply(response_text)
                        
                        # Log the successful response
                        self.activity_logger.log_response(
                            post_id=post.id,
                            post_title=post.title,
                            subreddit=subreddit,
                            comment_id=comment.id,
                            comment_text=response_text,
                            relevance_score=post_data['relevance_score'],
                            keywords=post_data['matched_keywords'],
                            status="success"
                        )
                        
                        # Update counters
                        self.responses_today += 1
                        self.subreddit_responses[subreddit] = self.subreddit_responses.get(subreddit, 0) + 1
                        
                        self.logger.info(f"Posted response to {post.id} in r/{subreddit}")
                        
                    except prawcore.exceptions.Forbidden:
                        self.logger.error(f"Forbidden to comment on post {post.id} in r/{subreddit}")
                        self.activity_logger.log_response(
                            post_id=post.id, 
                            post_title=post.title,
                            subreddit=subreddit,
                            comment_id=None,
                            comment_text=response_text,
                            relevance_score=post_data['relevance_score'],
                            keywords=post_data['matched_keywords'],
                            status="forbidden"
                        )
                    except Exception as e:
                        self.logger.error(f"Error posting comment: {str(e)}")
                        self.activity_logger.log_response(
                            post_id=post.id, 
                            post_title=post.title,
                            subreddit=subreddit,
                            comment_id=None,
                            comment_text=response_text,
                            relevance_score=post_data['relevance_score'],
                            keywords=post_data['matched_keywords'],
                            status="error",
                            error=str(e)
                        )
            
            self.logger.info(f"Cycle completed. Posted {self.responses_today} responses today")
            
        except prawcore.exceptions.ResponseException as e:
            self.logger.error(f"Reddit API error: {str(e)}")
        except prawcore.exceptions.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error in bot cycle: {str(e)}", exc_info=True)
