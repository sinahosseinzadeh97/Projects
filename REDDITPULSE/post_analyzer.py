"""
Post analyzer module to determine relevance of Reddit posts
"""
import logging
import re
from collections import Counter

class PostAnalyzer:
    """Analyzes Reddit posts for relevance to target keywords/topics"""
    
    def __init__(self, keywords):
        """
        Initialize the analyzer with target keywords
        
        Args:
            keywords (dict): Dictionary with topic categories as keys and lists of keywords as values
        """
        self.logger = logging.getLogger(__name__)
        self.keywords = keywords
        
        # Flatten keyword lists and precompile regex patterns
        self.all_keywords = []
        self.keyword_patterns = {}
        
        for category, terms in self.keywords.items():
            for term in terms:
                if term not in self.all_keywords:
                    self.all_keywords.append(term)
                    # Create a case-insensitive word boundary pattern
                    self.keyword_patterns[term] = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                    
        self.logger.info(f"Post analyzer initialized with {len(self.all_keywords)} keywords")
    
    def analyze_post(self, post):
        """
        Analyze a Reddit post for relevance
        
        Args:
            post (praw.models.Submission): The Reddit post to analyze
            
        Returns:
            tuple: (relevance_score, matched_keywords)
                - relevance_score (float): A score from 0.0 to 1.0 indicating relevance
                - matched_keywords (list): List of keywords that matched in the post
        """
        # Combine title and post content for analysis
        content = f"{post.title} {post.selftext}"
        
        # Find matching keywords
        matched_keywords = []
        
        for keyword, pattern in self.keyword_patterns.items():
            if pattern.search(content):
                matched_keywords.append(keyword)
        
        # Calculate basic relevance score
        relevance_score = len(matched_keywords) / max(len(self.all_keywords) * 0.1, 1)
        
        # Cap score at 1.0
        relevance_score = min(relevance_score, 1.0)
        
        # Log the result
        self.logger.debug(f"Post {post.id} scored {relevance_score:.2f} with matches: {', '.join(matched_keywords)}")
        
        return relevance_score, matched_keywords
            
    def get_top_topics(self, matched_keywords, top_n=2):
        """
        Determine the top topic categories for the matched keywords
        
        Args:
            matched_keywords (list): List of keywords that matched in a post
            top_n (int): Number of top topics to return
            
        Returns:
            list: List of top topic categories
        """
        topic_matches = Counter()
        
        for topic, keywords in self.keywords.items():
            for keyword in matched_keywords:
                if keyword in keywords:
                    topic_matches[topic] += 1
        
        # Get the top N topics
        top_topics = [topic for topic, _ in topic_matches.most_common(top_n)]
        
        return top_topics
