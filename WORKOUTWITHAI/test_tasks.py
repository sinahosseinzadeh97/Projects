import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Celery tasks
from tasks.tasks import analyze_video, cleanup_old_videos, generate_user_stats

class TestCeleryTasks:
    @patch('tasks.tasks.WorkoutAnalyzer')
    @patch('tasks.tasks.crud.update_workout_analysis')
    @patch('tasks.tasks.database.SessionLocal')
    def test_analyze_video(self, mock_session_local, mock_update_workout, mock_analyzer):
        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock workout analyzer
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.analyze_video.return_value = {
            "dominant_exercise": "squat",
            "calories_burned": 15.5,
            "exercise_counts": {"squat": 10, "pushup": 5},
            "processing_time": 10.5,
            "total_frames": 100,
            "output_video": "/tmp/analysis/annotated_video.mp4"
        }
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Test analyze_video task
        result = analyze_video(1, "/tmp/test_video.mp4")
        
        # Verify results
        assert result["status"] == "success"
        assert result["workout_id"] == 1
        assert result["results"]["dominant_exercise"] == "squat"
        assert result["results"]["calories_burned"] == 15.5
        
        # Verify database updates
        assert mock_update_workout.call_count == 2
        mock_update_workout.assert_any_call(mock_db, 1, "processing")
        
    @patch('tasks.tasks.database.SessionLocal')
    def test_cleanup_old_videos(self, mock_session_local):
        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Test cleanup_old_videos task
        result = cleanup_old_videos(30)
        
        # Verify results
        assert result["status"] == "success"
        assert "Cleaned up videos older than 30 days" in result["message"]
        
    @patch('tasks.tasks.crud.get_user_workouts')
    @patch('tasks.tasks.database.SessionLocal')
    def test_generate_user_stats(self, mock_session_local, mock_get_workouts):
        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock user workouts
        mock_workout1 = MagicMock()
        mock_workout1.analysis_results = {"calories_burned": 10.5}
        mock_workout2 = MagicMock()
        mock_workout2.analysis_results = {"calories_burned": 15.0}
        mock_get_workouts.return_value = [mock_workout1, mock_workout2]
        
        # Test generate_user_stats task
        result = generate_user_stats(1)
        
        # Verify results
        assert result["status"] == "success"
        assert result["user_id"] == 1
        assert result["stats"]["total_workouts"] == 2
        assert result["stats"]["total_calories"] == 25.5
