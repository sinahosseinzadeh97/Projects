"""
Test mode for the Reddit Automation Bot
For demonstration purposes when full Reddit API credentials are not available
"""
import random
import json
import os
from datetime import datetime, timedelta
from logger import ActivityLogger

class TestPost:
    """Simulated Reddit post for testing"""
    def __init__(self, id, title, selftext, subreddit_name, created_utc, score=5):
        self.id = id
        self.title = title
        self.selftext = selftext
        self.subreddit = TestSubreddit(subreddit_name)
        self.created_utc = created_utc
        self.score = score

class TestSubreddit:
    """Simulated Reddit subreddit for testing"""
    def __init__(self, name):
        self.display_name = name

class SimulatedTester:
    """
    Simulates the behavior of the Reddit automation bot for testing/demo purposes
    without requiring actual Reddit API credentials
    """
    
    def __init__(self):
        self.logger = ActivityLogger()
        self.sample_posts = self._load_sample_posts()
        
    def _load_sample_posts(self):
        """Load or create sample posts for testing"""
        sample_posts = [
            {
                "id": "test1",
                "title": "Looking for natural remedies for joint pain",
                "selftext": "I've been experiencing joint pain in my knees and elbows. I'm looking for natural remedies instead of taking pain medication. Any suggestions?",
                "subreddit": "alternativemedicine",
                "created_utc": (datetime.now() - timedelta(hours=3)).timestamp(),
                "score": 12
            },
            {
                "id": "test2",
                "title": "Best supplements for energy and focus?",
                "selftext": "I've been feeling tired and unfocused lately. Can anyone recommend some good supplements that might help with energy and mental clarity?",
                "subreddit": "supplements",
                "created_utc": (datetime.now() - timedelta(hours=5)).timestamp(),
                "score": 8
            },
            {
                "id": "test3",
                "title": "How to improve overall wellness with diet?",
                "selftext": "I'm trying to improve my overall health and wellness through my diet. What are some key foods or principles I should consider?",
                "subreddit": "wellness",
                "created_utc": (datetime.now() - timedelta(hours=2)).timestamp(),
                "score": 15
            },
            {
                "id": "test4",
                "title": "Meditation techniques for beginners",
                "selftext": "I'm new to meditation and looking for simple techniques to start with for stress reduction and mindfulness.",
                "subreddit": "wellness",
                "created_utc": (datetime.now() - timedelta(hours=4)).timestamp(),
                "score": 10
            },
            {
                "id": "test5",
                "title": "Herbal tea recommendations for sleep",
                "selftext": "I'm having trouble sleeping and would like to try some herbal teas that might help. What do you recommend?",
                "subreddit": "naturalremedies",
                "created_utc": (datetime.now() - timedelta(hours=6)).timestamp(), 
                "score": 6
            }
        ]
        
        return [TestPost(
            p["id"],
            p["title"],
            p["selftext"],
            p["subreddit"],
            p["created_utc"],
            p["score"]
        ) for p in sample_posts]
    
    def get_sample_posts(self):
        """Return sample posts for testing"""
        return self.sample_posts
    
    def run_test(self, analyzer, response_generator):
        """
        Run a simulated test of the bot's functionality
        
        Args:
            analyzer: PostAnalyzer instance
            response_generator: ResponseGenerator instance
        """
        print("Starting simulated test with sample posts...")
        
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")
            
        # Map subreddits to template categories for test mode
        subreddit_to_category = {
            'alternativemedicine': 'alternative_medicine',
            'naturalremedies': 'alternative_medicine',
            'wellness': 'wellness',
            'health': 'health',
            'supplements': 'health',
            'nutrition': 'health'
        }
            
        for post in self.sample_posts:
            # Analyze post
            relevance_score, matched_keywords = analyzer.analyze_post(post)
            
            # Only proceed if post is relevant (above 0.3 threshold)
            if relevance_score >= 0.3:
                # Generate response
                response_text, template_id, variant = response_generator.generate_response(
                    post.title, 
                    post.selftext,
                    matched_keywords
                )
                
                # If no template_id was generated, create a fake one for testing
                if not template_id:
                    # Match subreddit to template category
                    category = subreddit_to_category.get(post.subreddit.display_name.lower(), 'health')
                    template_id = f"{category}_{random.randint(1, 3)}"
                    variant = random.choice(['A', 'B'])
                
                # Simulate comment ID (would come from Reddit API in real usage)
                comment_id = f"t1_{random.randint(10000000, 99999999)}"
                
                # Only proceed if a response was generated
                if response_text:
                    # Log the response with explicit template_id and variant
                    self.logger.log_response(
                        post.id,
                        post.title,
                        post.subreddit.display_name,
                        comment_id,
                        response_text,
                        relevance_score,
                        matched_keywords,
                        "success",
                        extra_data={
                            "template_id": template_id,
                            "variant": variant
                        }
                    )
                    
                    print(f"Responded to post in r/{post.subreddit.display_name}: {post.title}")
                    print(f"Response (Template {template_id}, Variant {variant}): {response_text[:100]}...\n")
                else:
                    print(f"No suitable response template for post in r/{post.subreddit.display_name}: {post.title}")
            else:
                print(f"Skipped post (low relevance score {relevance_score}): {post.title}")
        
        print("Simulated test complete!")