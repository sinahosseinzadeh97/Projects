"""
Subreddit monitoring module to fetch new posts from targeted subreddits
"""
import logging
import praw
from datetime import datetime, timedelta
import prawcore
import config

class SubredditMonitor:
    """Monitors subreddits for new posts matching criteria"""
    
    def __init__(self, subreddits):
        """
        Initialize the monitor with target subreddits
        
        Args:
            subreddits (list): List of subreddit names to monitor
        """
        self.logger = logging.getLogger(__name__)
        self.subreddits = subreddits
        
        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            username=config.REDDIT_USERNAME,
            password=config.REDDIT_PASSWORD,
            user_agent=config.REDDIT_USER_AGENT
        )
        
        # Keep track of processed posts to avoid duplicates
        self.processed_posts = set()
        
        self.logger.info(f"Subreddit monitor initialized for: {', '.join(subreddits)}")
    
    def get_new_posts(self, limit=25):
        """
        Fetch new posts from the targeted subreddits
        
        Args:
            limit (int): Maximum number of posts to fetch from each subreddit
            
        Returns:
            list: A list of praw.models.Submission objects
        """
        all_posts = []
        cutoff_time = datetime.now() - timedelta(hours=config.MAX_POST_AGE_HOURS)
        
        for subreddit_name in self.subreddits:
            try:
                self.logger.info(f"Fetching posts from r/{subreddit_name}")
                
                subreddit = self.reddit.subreddit(subreddit_name)
                new_posts = subreddit.new(limit=limit)
                
                for post in new_posts:
                    # Skip if we've already processed this post
                    if post.id in self.processed_posts:
                        continue
                    
                    # Skip if post is too old
                    post_time = datetime.fromtimestamp(post.created_utc)
                    if post_time < cutoff_time:
                        continue
                    
                    # Skip if post has no content
                    if not post.selftext or len(post.selftext) < 10:
                        continue
                    
                    # Add to posts list and mark as processed
                    all_posts.append(post)
                    self.processed_posts.add(post.id)
                
                self.logger.debug(f"Found {len(all_posts)} new posts in r/{subreddit_name}")
                
            except prawcore.exceptions.Redirect:
                self.logger.error(f"Subreddit r/{subreddit_name} does not exist or is private")
            except prawcore.exceptions.ResponseException as e:
                self.logger.error(f"Reddit API error for r/{subreddit_name}: {str(e)}")
            except Exception as e:
                self.logger.error(f"Error fetching posts from r/{subreddit_name}: {str(e)}")
        
        # Prevent the processed posts set from growing too large
        if len(self.processed_posts) > 10000:
            self.logger.info("Trimming processed posts cache")
            self.processed_posts = set(list(self.processed_posts)[-5000:])
            
        return all_posts
