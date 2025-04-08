"""
Web dashboard for monitoring bot performance and logs
"""
import os
import logging
import pandas as pd
from datetime import datetime, timedelta
import json
from flask import Flask, render_template, jsonify, request, make_response
from flask_cors import CORS
from logger import ActivityLogger
import config

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)
app.secret_key = os.environ.get("SESSION_SECRET", "reddit-bot-dashboard-secret")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize activity logger
activity_logger = ActivityLogger()

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/logs')
def logs():
    """Render the logs page"""
    return render_template('logs.html')

@app.route('/settings')
def settings():
    """Render the settings page"""
    return render_template('settings.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint for the API"""
    return jsonify({
        'status': 'ok',
        'message': 'Reddit Automation Bot API is operational',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
def get_stats():
    """API endpoint to get bot statistics"""
    try:
        # Get statistics from the logger
        stats = activity_logger.get_stats(days=7)
        
        # Format dates for JSON serialization
        if 'daily_activity' in stats:
            stats['daily_activity'] = {str(date): count for date, count in stats['daily_activity'].items()}
        
        # Add empty data if some keys are missing
        for key in ['total_responses', 'successful_responses', 'failed_responses', 
                    'success_rate', 'tracked_subreddits', 'avg_relevance', 
                    'response_change', 'success_rate_change']:
            if key not in stats:
                stats[key] = 0
                
        if 'daily_activity' not in stats:
            stats['daily_activity'] = {}
            
        if 'subreddit_activity' not in stats:
            stats['subreddit_activity'] = {}
        
        logger.debug(f"Returning stats data: {stats}")
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/ab-testing')
def get_ab_testing():
    """API endpoint to get A/B testing results"""
    try:
        # Get the category to filter by
        category = request.args.get('category', 'all')
        days = int(request.args.get('days', '30'))
        
        # Get statistics from the logger
        stats = activity_logger.get_stats(days=days)
        
        # Extract A/B testing data
        ab_data = {
            'overall': {
                'variant_a': {
                    'count': stats.get('variant_a_count', 0),
                    'success_rate': stats.get('variant_a_success_rate', 0),
                    'avg_relevance': stats.get('variant_a_relevance', 0.0)
                },
                'variant_b': {
                    'count': stats.get('variant_b_count', 0),
                    'success_rate': stats.get('variant_b_success_rate', 0),
                    'avg_relevance': stats.get('variant_b_relevance', 0.0)
                }
            },
            'categories': {}
        }
        
        # Add category-specific data if available
        if 'category_stats' in stats:
            categories = stats['category_stats']
            
            if category != 'all':
                # Only include the requested category
                if category in categories:
                    cat_data = categories[category]
                    ab_data['categories'][category] = {
                        'variant_a': {
                            'count': cat_data.get('variant_a_count', 0),
                            'success_rate': cat_data.get('variant_a_success_rate', 0),
                            'avg_relevance': cat_data.get('variant_a_relevance', 0.0)
                        },
                        'variant_b': {
                            'count': cat_data.get('variant_b_count', 0),
                            'success_rate': cat_data.get('variant_b_success_rate', 0),
                            'avg_relevance': cat_data.get('variant_b_relevance', 0.0)
                        }
                    }
            else:
                # Include all categories
                for cat, cat_data in categories.items():
                    ab_data['categories'][cat] = {
                        'variant_a': {
                            'count': cat_data.get('variant_a_count', 0),
                            'success_rate': cat_data.get('variant_a_success_rate', 0),
                            'avg_relevance': cat_data.get('variant_a_relevance', 0.0)
                        },
                        'variant_b': {
                            'count': cat_data.get('variant_b_count', 0),
                            'success_rate': cat_data.get('variant_b_success_rate', 0),
                            'avg_relevance': cat_data.get('variant_b_relevance', 0.0)
                        }
                    }
        
        # Fallback options - Include default categories if none are available
        if not ab_data['categories']:
            default_categories = ['health', 'wellness', 'alternative_medicine']
            for cat in default_categories:
                ab_data['categories'][cat] = {
                    'variant_a': {
                        'count': 0,
                        'success_rate': 0,
                        'avg_relevance': 0.0
                    },
                    'variant_b': {
                        'count': 0,
                        'success_rate': 0,
                        'avg_relevance': 0.0
                    }
                }
                
        logger.debug(f"Returning A/B testing data: {ab_data}")
        
        return jsonify({
            'status': 'success',
            'data': ab_data
        })
    except Exception as e:
        logger.error(f"Error retrieving A/B testing data: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/logs/recent')
def get_recent_logs():
    """API endpoint to get recent log entries"""
    try:
        # Load the last 50 entries from the JSON log
        with open(activity_logger.json_log_file, 'r') as f:
            logs = json.load(f)
        
        # Return the most recent entries
        recent_logs = logs[-50:] if logs else []
        
        # Log request and response for debugging
        logger.debug(f"Returning {len(recent_logs)} recent log entries")
        
        return jsonify({
            'status': 'success',
            'data': recent_logs
        })
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}", exc_info=True)
        
        # Try to create an empty log file if it doesn't exist
        if not os.path.exists(activity_logger.json_log_file):
            try:
                os.makedirs(os.path.dirname(activity_logger.json_log_file), exist_ok=True)
                with open(activity_logger.json_log_file, 'w') as f:
                    json.dump([], f)
                logger.info(f"Created empty JSON log file: {activity_logger.json_log_file}")
            except Exception as create_error:
                logger.error(f"Failed to create log file: {str(create_error)}")
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/subreddit-performance')
def get_subreddit_performance():
    """API endpoint to get performance by subreddit"""
    try:
        # Load CSV data
        df = pd.read_csv(activity_logger.csv_log_file)
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_df = df[df['timestamp'] > cutoff_date]
        
        # Group by subreddit and status
        performance = recent_df.groupby(['subreddit', 'status']).size().unstack(fill_value=0).reset_index()
        
        # Calculate success rate
        if 'success' in performance.columns:
            performance['total'] = performance.sum(axis=1, numeric_only=True)
            performance['success_rate'] = performance['success'] / performance['total']
        else:
            performance['success'] = 0
            performance['total'] = 0
            performance['success_rate'] = 0
        
        return jsonify({
            'status': 'success',
            'data': performance.to_dict(orient='records')
        })
    except Exception as e:
        logger.error(f"Error retrieving subreddit performance: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
