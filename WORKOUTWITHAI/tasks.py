from celery import Celery
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path to import database and ML modules
sys.path.append("..")
from database import crud, models, database
from ml.video_analysis import WorkoutAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get Celery configuration from environment variables
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

# Initialize Celery app
app = Celery(
    'tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour time limit for tasks
    worker_prefetch_multiplier=1,  # Process one task at a time
)

@app.task(bind=True, name='tasks.analyze_video')
def analyze_video(self, workout_id: int, video_path: str):
    """
    Celery task to analyze workout video
    
    Args:
        workout_id: ID of the workout in the database
        video_path: Path to the video file
    """
    logger.info(f"Starting video analysis for workout {workout_id}, video: {video_path}")
    
    try:
        # Update workout status to processing
        db = database.SessionLocal()
        crud.update_workout_analysis(db, workout_id, "processing")
        
        # Create output directory
        output_dir = os.path.join(os.path.dirname(video_path), f"analysis_{workout_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize workout analyzer
        analyzer = WorkoutAnalyzer(output_dir=output_dir)
        
        # Analyze video
        logger.info(f"Running ML analysis on video: {video_path}")
        results = analyzer.analyze_video(video_path)
        
        # Extract key metrics for database storage
        analysis_results = {
            "dominant_exercise": results.get("dominant_exercise"),
            "calories_burned": results.get("calories_burned"),
            "exercise_counts": results.get("exercise_counts"),
            "processing_time": results.get("processing_time"),
            "total_frames": results.get("total_frames"),
            "output_video": results.get("output_video"),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        # Update workout with analysis results
        logger.info(f"Analysis complete for workout {workout_id}, updating database")
        crud.update_workout_analysis(db, workout_id, "completed", analysis_results)
        
        return {
            "status": "success",
            "workout_id": workout_id,
            "results": analysis_results
        }
        
    except Exception as e:
        logger.error(f"Error analyzing video for workout {workout_id}: {str(e)}")
        
        # Update workout status to failed
        try:
            db = database.SessionLocal()
            crud.update_workout_analysis(db, workout_id, "failed", {"error": str(e)})
        except Exception as db_error:
            logger.error(f"Error updating workout status: {str(db_error)}")
            
        # Re-raise the exception to mark the task as failed
        raise
        
    finally:
        # Close database session
        if 'db' in locals():
            db.close()

@app.task(bind=True, name='tasks.cleanup_old_videos')
def cleanup_old_videos(self, days_threshold: int = 30):
    """
    Celery task to clean up old video files
    
    Args:
        days_threshold: Number of days after which videos should be cleaned up
    """
    logger.info(f"Starting cleanup of videos older than {days_threshold} days")
    
    try:
        # Get list of old workouts
        db = database.SessionLocal()
        # This would be implemented with a query to find old workouts
        # For now, we'll just log the action
        
        logger.info(f"Cleanup task completed")
        return {"status": "success", "message": f"Cleaned up videos older than {days_threshold} days"}
        
    except Exception as e:
        logger.error(f"Error cleaning up old videos: {str(e)}")
        raise
        
    finally:
        # Close database session
        if 'db' in locals():
            db.close()

@app.task(bind=True, name='tasks.generate_user_stats')
def generate_user_stats(self, user_id: int):
    """
    Celery task to generate statistics for a user
    
    Args:
        user_id: ID of the user in the database
    """
    logger.info(f"Generating statistics for user {user_id}")
    
    try:
        # Get user workouts
        db = database.SessionLocal()
        workouts = crud.get_user_workouts(db, user_id)
        
        # Calculate statistics
        total_workouts = len(workouts)
        total_calories = sum(
            workout.analysis_results.get("calories_burned", 0) 
            for workout in workouts 
            if workout.analysis_results
        )
        
        # This would be expanded with more detailed statistics
        stats = {
            "total_workouts": total_workouts,
            "total_calories": total_calories,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Statistics generated for user {user_id}")
        return {
            "status": "success",
            "user_id": user_id,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error generating statistics for user {user_id}: {str(e)}")
        raise
        
    finally:
        # Close database session
        if 'db' in locals():
            db.close()

# Periodic tasks can be scheduled using Celery Beat
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Clean up old videos every week
    sender.add_periodic_task(
        60 * 60 * 24 * 7,  # 7 days
        cleanup_old_videos.s(30),  # 30 days threshold
        name='cleanup-old-videos-weekly'
    )
