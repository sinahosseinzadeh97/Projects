"""
Logging module for tracking bot activity and performance
"""
import logging
import json
import csv
import os
from datetime import datetime, timedelta
import pandas as pd
import config

class ActivityLogger:
    """Logs and tracks bot activity"""
    
    def __init__(self):
        """Initialize the activity logger"""
        self.logger = logging.getLogger(__name__)
        
        # Create logs directory
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)
        
        # Set log file paths if they don't include a directory
        self.json_log_file = config.JSON_LOG_FILE
        self.csv_log_file = config.CSV_LOG_FILE
        
        # Add logs directory to log files if they don't have a directory
        if not os.path.dirname(self.json_log_file):
            self.json_log_file = os.path.join(logs_dir, self.json_log_file)
            
        if not os.path.dirname(self.csv_log_file):
            self.csv_log_file = os.path.join(logs_dir, self.csv_log_file)
        
        # Initialize files if they don't exist
        self._initialize_json_log()
        self._initialize_csv_log()
        
        self.logger.info("Activity logger initialized")
    
    def _initialize_json_log(self):
        """Initialize JSON log file if it doesn't exist"""
        if not os.path.exists(self.json_log_file):
            with open(self.json_log_file, 'w') as f:
                json.dump([], f)
    
    def _initialize_csv_log(self):
        """Initialize CSV log file if it doesn't exist"""
        if not os.path.exists(self.csv_log_file):
            with open(self.csv_log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'post_id', 'post_title', 'subreddit', 
                    'comment_id', 'relevance_score', 'keywords', 
                    'status', 'template_id', 'variant', 'error'
                ])
    
    def log_response(self, post_id, post_title, subreddit, comment_id, 
                    comment_text, relevance_score, keywords, status, error=None, extra_data=None):
        """
        Log a bot response to both JSON and CSV logs
        
        Args:
            post_id (str): Reddit post ID
            post_title (str): Title of the post
            subreddit (str): Subreddit name
            comment_id (str): ID of the posted comment (None if failed)
            comment_text (str): Text of the response
            relevance_score (float): Relevance score of the post
            keywords (list): Keywords that matched in the post
            status (str): Status of the response (success/error/forbidden)
            error (str, optional): Error message if status is error
            extra_data (dict, optional): Additional data to include in the log entry
        """
        timestamp = datetime.now().isoformat()
        
        # Create log entry
        log_entry = {
            'timestamp': timestamp,
            'post_id': post_id,
            'post_title': post_title,
            'subreddit': subreddit,
            'comment_id': comment_id,
            'comment_text': comment_text,
            'relevance_score': relevance_score,
            'keywords': keywords,
            'status': status
        }
        
        if error:
            log_entry['error'] = error
            
        # Add any extra data
        if extra_data and isinstance(extra_data, dict):
            log_entry.update(extra_data)
        
        # Add to JSON log
        try:
            with open(self.json_log_file, 'r') as f:
                logs = json.load(f)
            
            logs.append(log_entry)
            
            with open(self.json_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error writing to JSON log: {str(e)}")
        
        # Add to CSV log - Include template_id and variant if available
        try:
            with open(self.csv_log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                
                # Extract extra fields for CSV
                template_id = extra_data.get('template_id', 'N/A') if extra_data else 'N/A'
                variant = extra_data.get('variant', 'N/A') if extra_data else 'N/A'
                
                writer.writerow([
                    timestamp,
                    post_id,
                    post_title[:50],  # Truncate long titles
                    subreddit,
                    comment_id or 'N/A',
                    relevance_score,
                    ','.join(keywords),
                    status,
                    template_id,
                    variant,
                    error or 'N/A'
                ])
        except Exception as e:
            self.logger.error(f"Error writing to CSV log: {str(e)}")
        
        template_info = ""
        if extra_data and 'template_id' in extra_data:
            template_info = f" using template {extra_data['template_id']} (variant {extra_data.get('variant', 'A')})"
            
        self.logger.info(f"Logged {status} response to post {post_id} in r/{subreddit}{template_info}")
    
    def get_stats(self, days=7):
        """
        Get statistics about bot performance
        
        Args:
            days (int): Number of days to include in stats
            
        Returns:
            dict: Dictionary of statistics
        """
        try:
            # Load CSV log into pandas
            df = pd.read_csv(self.csv_log_file)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter for last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_df = df[df['timestamp'] > cutoff_date]
            
            # Basic statistics
            total_responses = len(recent_df)
            successful_responses = len(recent_df[recent_df['status'] == 'success'])
            success_rate = (successful_responses / max(total_responses, 1)) * 100
            
            # Calculate statistics
            stats = {
                'total_responses': total_responses,
                'successful_responses': successful_responses,
                'failed_responses': len(recent_df[recent_df['status'] != 'success']),
                'success_rate': int(success_rate),
                'subreddit_activity': recent_df['subreddit'].value_counts().to_dict(),
                'daily_activity': recent_df.groupby(recent_df['timestamp'].dt.date).size().to_dict(),
                'tracked_subreddits': len(recent_df['subreddit'].unique()),
                'avg_relevance': float(recent_df['relevance_score'].mean())
            }
            
            # Add A/B testing statistics
            if 'variant' in recent_df.columns:
                # Get variant statistics
                variant_a = recent_df[recent_df['variant'] == 'A']
                variant_b = recent_df[recent_df['variant'] == 'B']
                
                # Overall variant counts
                stats['variant_a_count'] = len(variant_a)
                stats['variant_b_count'] = len(variant_b)
                
                # Success rates by variant
                variant_a_success = len(variant_a[variant_a['status'] == 'success'])
                variant_b_success = len(variant_b[variant_b['status'] == 'success'])
                
                stats['variant_a_success_rate'] = int((variant_a_success / max(len(variant_a), 1)) * 100)
                stats['variant_b_success_rate'] = int((variant_b_success / max(len(variant_b), 1)) * 100)
                
                # Average relevance by variant
                stats['variant_a_relevance'] = float(variant_a['relevance_score'].mean()) if len(variant_a) > 0 else 0
                stats['variant_b_relevance'] = float(variant_b['relevance_score'].mean()) if len(variant_b) > 0 else 0
                
                # Stats by template category
                if 'template_id' in recent_df.columns:
                    # Extract category from template_id (e.g., "health_1" -> "health")
                    recent_df['category'] = recent_df['template_id'].apply(
                        lambda x: x.split('_')[0] if isinstance(x, str) and '_' in x else 'unknown'
                    )
                    
                    # Get categories
                    categories = recent_df['category'].unique().tolist()
                    category_stats = {}
                    
                    for category in categories:
                        if category != 'unknown' and category != 'N/A':
                            category_df = recent_df[recent_df['category'] == category]
                            category_a = category_df[category_df['variant'] == 'A']
                            category_b = category_df[category_df['variant'] == 'B']
                            
                            category_stats[category] = {
                                'total': len(category_df),
                                'variant_a_count': len(category_a),
                                'variant_b_count': len(category_b),
                                'variant_a_success_rate': int((len(category_a[category_a['status'] == 'success']) / max(len(category_a), 1)) * 100),
                                'variant_b_success_rate': int((len(category_b[category_b['status'] == 'success']) / max(len(category_b), 1)) * 100),
                                'variant_a_relevance': float(category_a['relevance_score'].mean()) if len(category_a) > 0 else 0,
                                'variant_b_relevance': float(category_b['relevance_score'].mean()) if len(category_b) > 0 else 0,
                            }
                    
                    stats['category_stats'] = category_stats
            
            # Add change indicators
            # Calculate changes compared to previous period
            previous_start = cutoff_date - timedelta(days=days)
            previous_df = df[(df['timestamp'] > previous_start) & (df['timestamp'] <= cutoff_date)]
            
            previous_total = len(previous_df)
            stats['response_change'] = total_responses - previous_total
            
            previous_success_rate = (len(previous_df[previous_df['status'] == 'success']) / max(previous_total, 1)) * 100
            stats['success_rate_change'] = int(success_rate - previous_success_rate)
            
            return stats
        except Exception as e:
            self.logger.error(f"Error calculating stats: {str(e)}")
            return {
                'error': str(e),
                'total_responses': 0,
                'successful_responses': 0,
                'failed_responses': 0,
                'success_rate': 0,
                'subreddit_activity': {},
                'daily_activity': {},
                'tracked_subreddits': 0,
                'avg_relevance': 0.0,
                'response_change': 0,
                'success_rate_change': 0
            }
